#!/bin/bash
# Efficient AI Branch Cleanup using git commands
# Keeps 5 most recent branches, deletes the rest

echo "🧹 Efficient AI Branch Cleanup"
echo "================================"

# Get current count
CURRENT_COUNT=$(git branch -r | grep "ai-recommendation" | wc -l)
echo "📊 Current remote AI branches: $CURRENT_COUNT"

if [ $CURRENT_COUNT -le 5 ]; then
    echo "✅ Branch count is within limit ($CURRENT_COUNT <= 5)"
    exit 0
fi

echo "🗑️ Will delete $((CURRENT_COUNT - 5)) branches, keeping 5 most recent"

# Get the 5 most recent branches to keep
echo "📋 Identifying 5 most recent branches to keep..."
KEEP_BRANCHES=$(git branch -r | grep "ai-recommendation" | sort -k2 -r | head -5 | sed 's/origin\///')

echo "🔒 Keeping these branches:"
echo "$KEEP_BRANCHES"

# Get all AI branches except the ones we want to keep
echo "🗑️ Preparing to delete other branches..."
DELETE_BRANCHES=$(git branch -r | grep "ai-recommendation" | sed 's/origin\///' | grep -v -F "$KEEP_BRANCHES")

echo "📊 Branches to delete: $(echo "$DELETE_BRANCHES" | wc -l)"

# Delete branches in batches
echo "🚀 Starting batch deletion..."
BATCH_SIZE=50
COUNT=0

for branch in $DELETE_BRANCHES; do
    if [ -n "$branch" ]; then
        echo "Deleting: $branch"
        git push origin --delete "$branch" 2>/dev/null || echo "Failed to delete: $branch"
        COUNT=$((COUNT + 1))
        
        # Progress indicator
        if [ $((COUNT % 10)) -eq 0 ]; then
            echo "Progress: $COUNT branches deleted..."
        fi
    fi
done

echo "✅ Deletion complete! Deleted $COUNT branches"

# Final count
FINAL_COUNT=$(git branch -r | grep "ai-recommendation" | wc -l)
echo "📊 Final remote AI branch count: $FINAL_COUNT"

# Create consolidated branch
echo "📋 Creating consolidated branch..."
git checkout main
CONSOLIDATED_BRANCH="ai-recommendations-consolidated-$(date +%s)"
git checkout -b "$CONSOLIDATED_BRANCH"

# Create summary
cat > AI_RECOMMENDATIONS_SUMMARY.md << EOF
# AI Recommendations Consolidated Summary

Generated: $(date)
Total Branches Cleaned: $COUNT
Remaining Branches: $FINAL_COUNT

## Cleanup Summary
- Started with: $CURRENT_COUNT remote AI branches
- Deleted: $COUNT branches
- Kept: $FINAL_COUNT most recent branches
- Consolidated into: $CONSOLIDATED_BRANCH

## Kept Branches
$(echo "$KEEP_BRANCHES" | sed 's/^/- /')

## Next Steps
1. Review remaining branches for important changes
2. Implement automated merge process for approved recommendations
3. Set up monitoring to prevent future branch accumulation

---
*This cleanup preserves recent AI recommendations while removing excessive branches.*
EOF

git add AI_RECOMMENDATIONS_SUMMARY.md
git commit -m "Consolidated AI recommendations after cleanup ($COUNT branches deleted)"

echo "✅ Created consolidated branch: $CONSOLIDATED_BRANCH"
echo "🎯 Cleanup complete!"
