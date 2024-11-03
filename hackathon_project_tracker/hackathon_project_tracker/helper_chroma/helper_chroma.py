from __future__ import annotations

from typing import TYPE_CHECKING

import chromadb

from hackathon_project_tracker.otel import tracer

if TYPE_CHECKING:
    from hackathon_project_tracker.models.project import Project


SPAN_KEY: str = "chroma"


def set_up_client_from_tokens(
    tokens: dict[str, str],
) -> chromadb.api.ClientAPI | None:
    with tracer.start_as_current_span("set_up_client_from_tokens") as span:
        required_tokens: list[str] = ["CHROMA_TENANT", "CHROMA_DATABASE", "CHROMA_API_KEY"]
        missing_tokens = [token for token in required_tokens if not tokens.get(token)]
        for token in missing_tokens:
            span.add_event(
                name="missing_tokens-chroma",
                attributes={
                    "missing_token": token,
                },
            )

        if missing_tokens:
            return None

        return chromadb.HttpClient(
            ssl=True,
            host="api.trychroma.com",
            tenant=str(tokens.get("CHROMA_TENANT")),
            database=str(tokens.get("CHROMA_DATABASE")),
            headers={
                "x-chroma-token": str(tokens.get("CHROMA_API_KEY")),
            },
        )


def _get_metadata(
    item: Project,
    metadata_keys: list[str],
) -> dict:
    item_dict: dict = item.dict()
    return {
        key: item_dict[key]
        for key in metadata_keys
        if key in item_dict and item_dict[key] is not None
    }


def add_item(
    item: Project,
    item_id: str,
    item_document: str,
    metadata_keys: list[str],
    collection_name: str,
    client: chromadb.api.client.Client,
) -> None:
    span_name: str = f"{SPAN_KEY}-add_item"
    with tracer.start_as_current_span(span_name) as span:

        def _setup_medata() -> dict:
            _metadata = _get_metadata(
                item=item,
                metadata_keys=metadata_keys,
            )
            _metadata.update(
                {
                    "collection_name": collection_name,
                },
            )
            return _metadata

        span.add_event(
            name=f"{span_name}-queued",
            attributes={
                "item_id": item_id,
                "collection_name": collection_name,
            },
        )
        metadata: dict = _setup_medata()
        span.set_attributes(
            attributes=metadata,
        )
        span.add_event(
            name=f"{span_name}-started",
            attributes=metadata,
        )
        collection: chromadb.Collection = client.get_or_create_collection(
            name=collection_name,
        )
        collection.add(
            ids=[item_id],
            documents=[item_document],
            metadatas=[metadata],
        )
        span.add_event(
            name=f"{span_name}-completed",
            attributes=metadata,
        )


def get_items(
    query: str,
    n_results: int,
    collection_name: str,
    client: chromadb.api.client.Client,
) -> chromadb.QueryResult:
    with tracer.start_as_current_span("get_items") as span:
        attributes: dict = {
            "query": query,
            "collection_name": collection_name,
            "n_results": n_results,
        }
        span.set_attributes(attributes)
        span.add_event(
            name="get_items-started",
            attributes=attributes,
        )
        span.add_event(
            name="get_collection-started",
            attributes=attributes,
        )
        collection: chromadb.Collection = client.get_collection(
            name=collection_name,
        )
        span.add_event(
            name="get_collection-completed",
            attributes={
                "collection_name": collection_name,
            },
        )
        span.add_event(
            name="query-started",
            attributes=attributes,
        )
        result: chromadb.QueryResult = collection.query(
            query_texts=query,
            n_results=n_results,
        )
        span.add_event(
            name="query-completed",
        )
        return result
