"""
app/rag/rag_service.py
RAG pipeline: local sentence-transformers embeddings + Qdrant vector DB + Groq LLM.
No OpenAI required — fully free to run.
"""
import asyncio
from typing import Optional
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, Range, MatchValue, MatchAny,
)
from groq import Groq
from sqlalchemy.orm import Session
from app.config import get_settings
from app.logger import get_logger

settings = get_settings()
logger   = get_logger(__name__)

VECTOR_SIZE = 384   # all-MiniLM-L6-v2 output dimensions


class RagService:
    """
    Handles plan embedding, Qdrant upsert, semantic search, and LLM-augmented Q&A.
    Embedding model runs locally (downloads ~90 MB on first use).
    """

    _embedder: Optional[SentenceTransformer] = None   # class-level cache

    def __init__(self):
        self.qdrant     = QdrantClient(url=settings.qdrant_url)
        self.groq       = Groq(api_key=settings.groq_api_key)
        self.collection = settings.qdrant_collection


    def _get_embedder(self) -> SentenceTransformer:
        if RagService._embedder is None:
            logger.info("loading_embedding_model", model=settings.embedding_model)
            RagService._embedder = SentenceTransformer(settings.embedding_model)
        return RagService._embedder

    def _embed(self, texts: list[str]) -> list[list[float]]:
        model = self._get_embedder()
        return model.encode(texts, normalize_embeddings=True).tolist()


    def ensure_collection(self) -> None:
        existing = [c.name for c in self.qdrant.get_collections().collections]
        if self.collection not in existing:
            self.qdrant.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            # Payload indexes for fast filtering
            for field, schema in [
                ("download_mbps", "integer"),
                ("price_monthly",  "float"),
                ("isp_id",         "integer"),
            ]:
                self.qdrant.create_payload_index(
                    collection_name=self.collection,
                    field_name=field,
                    field_schema=schema,
                )
            logger.info("qdrant_collection_created", name=self.collection)


    def index_all_plans(self, session: Session) -> int:
        self.ensure_collection()

        from sqlalchemy import text
        rows = session.execute(text("""
            SELECT p.id, p.normalized_name, p.download_mbps, p.upload_mbps,
                   p.price_monthly, p.bundle_flags, p.plan_type,
                   p.is_unlimited, p.fup_gb, p.description,
                   i.name AS isp_name, i.id AS isp_id
            FROM plans p
            JOIN isps i ON i.id = p.isp_id
            WHERE p.status IN ('active', 'promotional')
        """)).fetchall()

        if not rows:
            logger.warning("no_plans_to_index")
            return 0

        batch_size = 64
        total = 0

        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            texts  = [self._build_plan_text(r) for r in batch]
            vectors = self._embed(texts)

            points = [
                PointStruct(
                    id=str(r.id),
                    vector=vectors[j],
                    payload={
                        "plan_id":        str(r.id),
                        "isp_id":         r.isp_id,
                        "isp_name":       r.isp_name,
                        "normalized_name": r.normalized_name,
                        "download_mbps":  r.download_mbps,
                        "price_monthly":  float(r.price_monthly),
                        "price_per_mbps": round(float(r.price_monthly) / r.download_mbps, 2),
                        "bundle_flags":   list(r.bundle_flags or []),
                        "plan_type":      r.plan_type,
                        "is_unlimited":   r.is_unlimited,
                        "text":           texts[j],
                    },
                )
                for j, r in enumerate(batch)
            ]

            self.qdrant.upsert(collection_name=self.collection, points=points)
            total += len(batch)
            logger.info("qdrant_batch_indexed", progress=f"{total}/{len(rows)}")

        logger.info("qdrant_indexing_complete", total=total)
        return total


    def search(
        self,
        query: str,
        min_speed:    Optional[int]   = None,
        max_speed:    Optional[int]   = None,
        max_price:    Optional[float] = None,
        bundle_flags: Optional[list[str]] = None,
        isp_ids:      Optional[list[int]] = None,
        limit: int = 5,
    ) -> list[dict]:
        """Semantic similarity search with optional structured filters."""
        [query_vector] = self._embed([query])

        must_conditions = []

        if min_speed is not None:
            must_conditions.append(
                FieldCondition(key="download_mbps", range=Range(gte=min_speed))
            )
        if max_speed is not None:
            must_conditions.append(
                FieldCondition(key="download_mbps", range=Range(lte=max_speed))
            )
        if max_price is not None:
            must_conditions.append(
                FieldCondition(key="price_monthly", range=Range(lte=max_price))
            )
        if isp_ids:
            must_conditions.append(
                FieldCondition(key="isp_id", match=MatchAny(any=isp_ids))
            )
        if bundle_flags:
            for flag in bundle_flags:
                must_conditions.append(
                    FieldCondition(key="bundle_flags", match=MatchValue(value=flag))
                )

        results = self.qdrant.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=limit,
            query_filter=Filter(must=must_conditions) if must_conditions else None,
            with_payload=True,
            score_threshold=0.35,
        )

        return [
            {
                **r.payload,
                "score": round(r.score, 4),
                "explanation": (
                    f"Matched \"{query}\" \u2192 {r.payload.get('isp_name')} "
                    f"{r.payload.get('normalized_name')}: "
                    f"{r.payload.get('download_mbps')} Mbps @ "
                    f"NPR {r.payload.get('price_monthly')}/mo"
                ),
            }
            for r in results
        ]


    def ask(self, question: str) -> dict:
        """
        Retrieve top matching plans then ask Groq LLM to answer the question
        using retrieved context — pure RAG pattern.
        """
        sources = self.search(question, limit=8)

        # Always inject WorldLink into context if not already present
        worldlink_in_sources = any(
            s.get("isp_name", "").lower() == "worldlink" or
            s.get("isp_id") == 1
            for s in sources
        )
        if not worldlink_in_sources:
            wl_sources = self.search(question, isp_ids=[1], limit=3)
            sources = sources[:5] + wl_sources

        if not sources:
            return {
                "answer":  "No matching plans found. Try broadening your search.",
                "sources": [],
            }

        context = "".join(
            f"[{i+1}] {s['isp_name']} \u2014 {s['normalized_name']}: "
            f"{s['download_mbps']} Mbps, NPR {s['price_monthly']}/mo, "
            f"bundles: {', '.join(s['bundle_flags']) or 'none'}, "
            f"{'Unlimited' if s.get('is_unlimited') else str(s.get('fup_gb', '?')) + ' GB FUP'}"
            for i, s in enumerate(sources)
        )

        response = self.groq.chat.completions.create(
            model=settings.groq_llm_model,
            max_tokens=350,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a competitive intelligence analyst for WorldLink Communications "
                        "(Nepal ISP). Answer questions about ISP plans using ONLY the provided "
                        "context. Be concise, factual, and highlight best value. "
                        "Always mention ISP name and price. Respond in 2-4 sentences."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nAvailable plans:\n{context}",
                },
            ],
        )

        return {
            "answer":  response.choices[0].message.content or "Unable to generate answer.",
            "sources": sources,
        }


    @staticmethod
    def _build_plan_text(row) -> str:
        # PATCHED
        bundle_text = (
            f"Includes: {', '.join(row.bundle_flags)}."
            if row.bundle_flags else "No additional bundles."
        )
        fup_text = (
            "Unlimited data, no FUP."
            if row.is_unlimited
            else (f"FUP limit: {row.fup_gb} GB per month." if row.fup_gb else "FUP terms not specified.")
        )
        return " ".join(filter(None, [
            f"{row.isp_name} internet plan: {row.normalized_name}.",
            f"Provider: {row.isp_name}.",
            f"Speed: {row.download_mbps} Mbps download internet connection.",
            f"Price: NPR {row.price_monthly} per month, monthly cost.",
            fup_text,
            bundle_text,
            f"Plan category: {row.plan_type} internet service.",
            f"Cost efficiency: NPR {round(float(row.price_monthly) / row.download_mbps, 2)} per Mbps, price per megabit.",
        ]))
