"""
RAG Module for domain knowledge retrieval.
Uses embeddings and vector search to provide relevant context to agents.
Always cites sources.
"""

import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


@dataclass
class RAGDocument:
    """A document in the RAG knowledge base."""

    doc_id: str
    content: str
    source: str
    metadata: Dict[str, Any]
    relevance_score: Optional[float] = None


@dataclass
class RAGResult:
    """Result from RAG retrieval."""

    query: str
    documents: List[RAGDocument]
    context_summary: str
    sources: List[str]


class RAGModule:
    """
    RAG module for retrieving domain knowledge.

    Capabilities:
    - Retrieve relevant documents based on semantic search
    - Provide domain fundamentals
    - Cite all sources
    - Support multiple knowledge domains

    Limitations (by design):
    - No open-ended web crawling
    - Pre-indexed knowledge only
    - Domain-specific collections
    """

    def __init__(
        self,
        persist_dir: str = "./data/chroma",
        embedding_model: str = "all-MiniLM-L6-v2",
        collection_name: str = "sapiens_knowledge"
    ):
        """Initialize RAG module."""

        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_dir,
                anonymized_telemetry=False
            )
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.collection_name = collection_name

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )

    def add_documents(
        self,
        documents: List[str],
        sources: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        doc_ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the knowledge base.

        Args:
            documents: List of document texts
            sources: List of source URLs or references
            metadatas: Optional metadata for each document
            doc_ids: Optional custom document IDs
        """

        if not documents:
            return

        # Generate IDs if not provided
        if doc_ids is None:
            doc_ids = [f"doc_{i}" for i in range(len(documents))]

        # Prepare metadata
        if metadatas is None:
            metadatas = [{} for _ in documents]

        # Add source to metadata
        for i, source in enumerate(sources):
            metadatas[i]["source"] = source

        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()

        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=doc_ids
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        domain_filter: Optional[str] = None
    ) -> RAGResult:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query
            top_k: Number of documents to retrieve
            domain_filter: Optional domain filter (e.g., "fintech", "healthcare")

        Returns:
            RAGResult with documents and sources
        """

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()

        # Prepare filter
        where_filter = None
        if domain_filter:
            where_filter = {"domain": domain_filter}

        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )

        # Parse results
        documents = []
        sources = set()

        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                content = results["documents"][0][i]
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if "distances" in results else None

                # Calculate relevance score (1 - cosine distance)
                relevance_score = 1 - distance if distance is not None else None

                source = metadata.get("source", "Unknown")
                sources.add(source)

                doc = RAGDocument(
                    doc_id=doc_id,
                    content=content,
                    source=source,
                    metadata=metadata,
                    relevance_score=relevance_score
                )
                documents.append(doc)

        # Create context summary
        context_summary = self._create_context_summary(documents)

        return RAGResult(
            query=query,
            documents=documents,
            context_summary=context_summary,
            sources=list(sources)
        )

    def _create_context_summary(self, documents: List[RAGDocument]) -> str:
        """Create a summary of retrieved documents with citations."""

        if not documents:
            return "No relevant information found."

        summary_parts = []

        for i, doc in enumerate(documents, 1):
            summary_parts.append(
                f"[{i}] {doc.content[:200]}... (Source: {doc.source})"
            )

        return "\n\n".join(summary_parts)

    def get_domain_fundamentals(self, domain: str) -> RAGResult:
        """
        Get fundamental knowledge about a domain.

        Args:
            domain: Domain name (e.g., "product management", "fintech")

        Returns:
            RAGResult with domain fundamentals
        """

        query = f"fundamental concepts and principles of {domain}"
        return self.retrieve(query, top_k=10, domain_filter=domain)

    def get_implementation_examples(
        self,
        project_type: str,
        role: str
    ) -> RAGResult:
        """
        Get examples of similar projects or implementations.

        Args:
            project_type: Type of project (research, product, campaign, startup)
            role: Target role

        Returns:
            RAGResult with examples
        """

        query = f"{project_type} project examples for {role} role"
        return self.retrieve(query, top_k=5)

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""

        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
