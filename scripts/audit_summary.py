import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from build_summary import (
    annotate_singletons,
    apply_image_review,
    load_image_review_index,
    reorder_singleton_section,
    stems_from_round,
)
from frequency import cluster_items, rank_clusters
from inventory import load_inventory


def main():
    items=[]
    for rnd in load_inventory()['rounds']:
        items.extend(stems_from_round(rnd))
    review = load_image_review_index()
    clusters=apply_image_review(cluster_items(items), review)
    clusters=annotate_singletons(clusters, items, review)
    # No per-year cap; preserve baseline singleton candidates and reorder by priority.
    ranked=reorder_singleton_section(rank_clusters(clusters))
    lines=[]
    for i,c in enumerate(ranked[:100],1):
        lines.append(
            f"## {i} category={c['category']} frequency={c['frequency_score']} "
            f"latest={c['latest_score']} stable={c['stable_key']}"
        )
        for m in sorted(c['members'],key=lambda x:(x['round'],x['num'])):
            lines.append(f"- {m['round']}#{m['num']}: {m.get('stem','')[:260]}")
        lines.append('')
    Path('/var/minis/workspace/interior-craft/out/summary_audit.txt').write_text('\n'.join(lines),encoding='utf-8')
    print('items',len(items),'reviewed_clusters',len(clusters),'top',min(100,len(ranked)))


if __name__=='__main__': main()
