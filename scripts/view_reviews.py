"""
Quick script to view and export user reviews.

Usage:
    python scripts/view_reviews.py          # View recent reviews
    python scripts/view_reviews.py --all    # Export all reviews to CSV
    python scripts/view_reviews.py --stats  # Show statistics
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import pandas as pd
from src.review_store import load_reviews, review_summary, get_engine
from sqlalchemy import text


def show_recent_reviews(limit: int = 20):
    """Display recent reviews in a formatted table."""
    print("\n" + "="*100)
    print(f"RECENT REVIEWS (Last {limit})")
    print("="*100 + "\n")
    
    reviews = load_reviews(limit=limit)
    if not reviews:
        print("No reviews found.")
        return
    
    df = pd.DataFrame(reviews)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 50)
    print(df.to_string(index=False))
    print()


def show_statistics():
    """Display review statistics."""
    print("\n" + "="*100)
    print("REVIEW STATISTICS")
    print("="*100 + "\n")
    
    summary = review_summary()
    print(f"Total Reviews:          {summary['total_reviews']}")
    print(f"Average Rating:         {summary['avg_rating']:.2f}" if summary.get('avg_rating') else "Average Rating:         N/A")
    print(f"Total Predictions:      {summary['total_predictions_logged']}")
    print()
    
    # Group by model
    reviews = load_reviews(limit=10000)
    if reviews:
        df = pd.DataFrame(reviews)
        print("\nBreakdown by Model:")
        model_stats = df.groupby('model_used').agg({
            'rating': ['count', 'mean'],
            'created_at': 'count'
        }).round(2)
        model_stats.columns = ['Count', 'Avg Rating', 'Total']
        print(model_stats)
        print()


def export_to_csv(output_file: str | None = None):
    """Export all reviews to CSV file."""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = ROOT / 'reports' / f'reviews_export_{timestamp}.csv'
    else:
        output_file = Path(output_file)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nExporting reviews to {output_file}...")
    reviews = load_reviews(limit=50000)
    
    if not reviews:
        print("No reviews to export.")
        return
    
    df = pd.DataFrame(reviews)
    df.to_csv(output_file, index=False)
    print(f"✓ Exported {len(df)} reviews to {output_file}")
    print()


def export_predictions_to_csv(output_file: str | None = None):
    """Export all prediction logs to CSV file."""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = ROOT / 'reports' / f'predictions_export_{timestamp}.csv'
    else:
        output_file = Path(output_file)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nExporting prediction logs to {output_file}...")
    
    from src.review_store import init_store
    init_store()
    
    engine = get_engine()
    query = """
    SELECT created_at, model_used, source, user_hash, horizon_days, predicted_used_gb, predicted_used_pct
    FROM prediction_logs
    ORDER BY created_at DESC
    """
    
    df = pd.read_sql(text(query), engine)
    
    if df.empty:
        print("No prediction logs to export.")
        return
    
    df.to_csv(output_file, index=False)
    print(f"✓ Exported {len(df)} prediction logs to {output_file}")
    print()


def main():
    parser = argparse.ArgumentParser(description='View and export user reviews and predictions.')
    parser.add_argument('--all', action='store_true', help='Export all reviews to CSV')
    parser.add_argument('--predictions', action='store_true', help='Export prediction logs to CSV')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--limit', type=int, default=20, help='Number of recent reviews to display')
    parser.add_argument('--output', type=str, help='Output file path for export')
    
    args = parser.parse_args()
    
    try:
        if args.stats:
            show_statistics()
        
        if args.all:
            export_to_csv(args.output)
        elif args.predictions:
            export_predictions_to_csv(args.output)
        else:
            show_recent_reviews(args.limit)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
