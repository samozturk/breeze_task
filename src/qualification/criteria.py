
class QualificationCriteria:
    allowed_types = [
        "bar", "wine bar", "cocktail bar", "cafe", "tavern",
        "pub", "brewery", "restaurant"
    ]
    excluded_keywords = ["fast food", "kebab", "burger", "michelin"]

    def __init__(self, min_rating=4.0, min_reviews=10):
        self.min_rating = min_rating
        self.min_reviews = min_reviews

    def is_qualified(self, venue):
        """
        Returns True if venue meets criteria, False otherwise.
        """
        name = venue.get("name", "").lower()
        type_ = venue.get("type", "").lower()
        rating = venue.get("rating", 0)
        review_count = venue.get("review_count", 0)

        # Basic Type Check
        if not any(t in type_ for t in self.allowed_types):
            return False

        # Exclusion Check
        if any(bad in name for bad in self.excluded_keywords):
            return False

        # Rating & Review Quality
        if rating < self.min_rating:
            return False

        if review_count < self.min_reviews:
            return False  # Optional: allow <10 reviews if rating is very high?

        return True

