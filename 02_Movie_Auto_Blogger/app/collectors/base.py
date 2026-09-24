"""Base movie collector and data provider interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NormalizedMovie(BaseModel):
    """Provider-agnostic normalized movie model."""
    external_id: str
    source: str = "tmdb"
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    genres: List[str] = Field(default_factory=list)
    original_language: Optional[str] = None
    popularity: Optional[float] = 0.0
    vote_average: Optional[float] = 0.0
    vote_count: Optional[int] = 0
    director: Optional[str] = None
    major_cast: List[str] = Field(default_factory=list)
    poster_reference: Optional[str] = None
    backdrop_reference: Optional[str] = None
    source_url: Optional[str] = None
    raw_json: Optional[Dict[str, Any]] = None

    # Global and Domestic Ratings
    imdb_id: Optional[str] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[str] = None
    rotten_tomatoes_score: Optional[str] = None
    metacritic_score: Optional[str] = None
    watcha_rating: Optional[float] = None
    naver_rating: Optional[float] = None
    naver_rating_type: Optional[str] = None
    naver_vote_count: Optional[str] = None

    # Scoring & explanation breakdown
    candidate_score: Optional[float] = None
    score_breakdown: Optional[Dict[str, float]] = None

    # Source attribution & licensing metadata
    source_attribution: str = "TMDB (The Movie Database)"


class BaseCollector(ABC):
    """Abstract collector interface for movie data providers."""

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check provider connectivity and return detailed status."""
        pass

    @abstractmethod
    async def get_popular_movies(self, page: int = 1) -> List[NormalizedMovie]:
        """Fetch currently popular movies."""
        pass

    @abstractmethod
    async def get_now_playing_movies(self, page: int = 1) -> List[NormalizedMovie]:
        """Fetch currently playing movies in theaters."""
        pass

    @abstractmethod
    async def get_upcoming_movies(self, page: int = 1) -> List[NormalizedMovie]:
        """Fetch upcoming movie releases."""
        pass

    async def get_korean_movies(self, years_back: int = 3, page: int = 1) -> List[NormalizedMovie]:
        """Fetch popular Korean movies from recent years."""
        return []

    async def get_ott_movies(self, page: int = 1) -> List[NormalizedMovie]:
        """Fetch popular OTT available movies in Korea."""
        return []

    @abstractmethod
    async def get_movie_details(self, movie_id: str) -> Optional[NormalizedMovie]:
        """Fetch detailed information for a specific movie."""
        pass

    @abstractmethod
    async def get_movie_credits(self, movie_id: str) -> Dict[str, Any]:
        """Fetch director and cast credits for a movie."""
        pass

    @abstractmethod
    async def get_image_metadata(self, movie_id: str) -> Dict[str, Any]:
        """Fetch available posters and backdrops metadata."""
        pass
