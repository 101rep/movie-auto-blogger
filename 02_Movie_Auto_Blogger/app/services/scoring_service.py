"""Candidate movie scoring and ranking engine."""
from datetime import datetime, date, timezone
import math
from typing import Dict, Tuple, Optional
from app.collectors.base import NormalizedMovie


class CandidateScoringService:
    """Calculates explainable candidate quality scores for movie selection.

    Formula:
        candidate_score = popularity_score + recency_score + rating_score
                        + completeness_score + youtube_bonus
    Score range: 0.0 ~ 110.0 (up to 10 pts YouTube bonus on top of 100)
    """

    @staticmethod
    def calculate_score(
        movie: NormalizedMovie,
        reference_date: Optional[date] = None,
        youtube_bonus: float = 0.0,
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate composite score and individual components for a movie.

        Args:
            movie: Normalized movie candidate.
            reference_date: Reference date for recency calculation (default: today UTC).
            youtube_bonus: Optional YouTube hype bonus (0.0–10.0) derived from
                trailer view/like/comment stats via YouTubeService.
        """
        ref = reference_date or datetime.now(timezone.utc).date()

        # 1. Popularity Score (0.0 ~ 35.0 pts)
        pop = max(float(movie.popularity or 0.0), 0.0)
        # Using log scale: pop 10 -> ~12.5, pop 50 -> ~20.5, pop 200 -> ~27.7, pop 1000+ -> 35.0
        popularity_score = round(min(35.0, math.log10(pop + 1.0) * 11.6), 2)

        # 2. Recency Score (0.0 ~ 30.0 pts)
        recency_score = 5.0
        if movie.release_date:
            try:
                rel_date = datetime.strptime(movie.release_date[:10], "%Y-%m-%d").date()
                delta_days = abs((ref - rel_date).days)
                if delta_days <= 30:
                    recency_score = 30.0  # Currently in theaters or immediate release
                elif delta_days <= 90:
                    recency_score = 22.0
                elif delta_days <= 180:
                    recency_score = 15.0
                elif delta_days <= 365:
                    recency_score = 10.0
                else:
                    recency_score = 5.0
            except ValueError:
                recency_score = 5.0

        # 3. Rating Score (0.0 ~ 20.0 pts)
        # Weighted by vote count confidence (need at least 100 votes for full rating weight)
        vote_avg = max(min(float(movie.vote_average or 0.0), 10.0), 0.0)
        vote_cnt = max(int(movie.vote_count or 0), 0)
        confidence = min(vote_cnt / 100.0, 1.0)
        rating_score = round(confidence * (vote_avg * 2.0), 2)

        # 4. Completeness Score (0.0 ~ 15.0 pts)
        completeness_score = 0.0
        if movie.overview and len(movie.overview.strip()) >= 30:
            completeness_score += 4.0
        if movie.poster_reference:
            completeness_score += 4.0
        if movie.director:
            completeness_score += 3.0
        if movie.major_cast and len(movie.major_cast) >= 3:
            completeness_score += 4.0

        # 5. YouTube Hype Bonus (0.0 ~ 10.0 pts)
        #    Derived from trailer view_count, like/view ratio, comment_count
        #    via YouTubeService.compute_youtube_opportunity_score()
        youtube_bonus_score = round(min(max(float(youtube_bonus), 0.0), 10.0), 2)

        total_score = round(
            popularity_score + recency_score + rating_score + completeness_score + youtube_bonus_score,
            2
        )

        breakdown = {
            "popularity_score": popularity_score,
            "recency_score": recency_score,
            "rating_score": rating_score,
            "completeness_score": completeness_score,
            "youtube_bonus": youtube_bonus_score,
            "total": total_score,
        }

        return total_score, breakdown
