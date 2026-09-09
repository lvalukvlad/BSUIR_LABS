def calculate_stats(tournaments):
    return {
        'total': len(tournaments),
        'total_prize': sum(t.prize_fund for t in tournaments),
        'sports_distribution': Counter(t.sport_type for t in tournaments),
        'top_winner': max(tournaments, key=lambda x: x.winner_earnings)
    }