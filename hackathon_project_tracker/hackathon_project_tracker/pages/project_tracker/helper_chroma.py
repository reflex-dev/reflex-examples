from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import chromadb

    from hackathon_project_tracker.models.project import Project

from hackathon_project_tracker import helper_chroma
from hackathon_project_tracker.otel import tracer


def chroma_add_project(
    project: Project,
    client: chromadb.api.client.Client,
) -> None:
    helper_chroma.add_item(
        item=project,
        item_id=str(project.repo_path),
        item_document=project.description,
        metadata_keys=[
            "repo_path",
            "stars",
            "language",
            "website",
            "description",
        ],
        collection_name="projects",
        client=client,
    )


def filter_by_distance(
    distances: list[list[float]],
    threshold: float,
) -> list[int]:
    """Filter Chroma results based on distance threshold.

    Args:
        distances: List of distance scores from Chroma query results
        threshold: Maximum distance threshold to include results

    Returns:
        List of indices where distance is below threshold
    """
    if not distances:
        return []

    # Return indices where distance is below threshold
    return [
        idx for idx, distance in enumerate(distances[0]) if distance <= threshold
    ]


def chroma_get_projects(
    repo_filter_vector_search_text: str,
    n_results: int,
    client: chromadb.api.client.Client,
    distance_threshold: float,
) -> list[str]:
    with tracer.start_as_current_span("get_projects") as span:
        span.add_event(
            name="get_projects-started",
            attributes={
                "query": repo_filter_vector_search_text,
                "n_results-input": n_results,
            },
        )
        result: chromadb.QueryResult = helper_chroma.get_items(
            query=repo_filter_vector_search_text,
            n_results=n_results,
            collection_name="projects",
            client=client,
        )
        span.add_event(
            name="get_projects-completed",
            attributes={
                "query": repo_filter_vector_search_text,
                "n_results-output": len(result.get("ids", [])),
            },
        )
        print(result)
        filtered_indices: list[int] = filter_by_distance(
            result.get("distances", []), distance_threshold,
        )
        filtered_results: list[str] = [result["ids"][0][i] for i in filtered_indices]
        return filtered_results
