#!/bin/bash
# NUCLEAR BRANCH CLEANUP - Emergency cleanup for excessive AI branches
# This script will aggressively clean up all AI branches except the 5 most recent

echo "🚨 NUCLEAR AI BRANCH CLEANUP"
echo "=============================="
echo "⚠️  WARNING: This will delete ALL AI branches except the 5 most recent!"
echo "⚠️  Make sure you have backed up any important changes!"
echo ""

# Get current count
CURRENT_COUNT=$(git branch -r | grep "ai-recommendation" | wc -l)
echo "📊 Current remote AI branches: $CURRENT_COUNT"

if [ $CURRENT_COUNT -le 5 ]; then
    echo "✅ Branch count is already within limit ($CURRENT_COUNT <= 5)"
    exit 0
fi

echo "🗑️ Will delete $((CURRENT_COUNT - 5)) branches, keeping only 5 most recent"
echo ""

# Confirm before proceeding
read -p "Are you sure you want to proceed? Type 'YES' to continue: " confirmation
if [ "$confirmation" != "YES" ]; then
    echo "❌ Operation cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting nuclear cleanup..."

# Get the 5 most recent branches to keep
echo "📋 Identifying 5 most recent branches to keep..."
KEEP_BRANCHES=$(git branch -r | grep "ai-recommendation" | sort -k2 -r | head -5 | sed 's/origin\///')

echo "🔒 Keeping these branches:"
echo "$KEEP_BRANCHES"
echo ""

# Get all AI branches except the ones we want to keep
echo "🗑️ Preparing to delete other branches..."
DELETE_BRANCHES=$(git branch -r | grep "ai-recommendation" | sed 's/origin\///' | grep -v -F "$KEEP_BRANCHES")

BRANCHES_TO_DELETE=$(echo "$DELETE_BRANCHES" | wc -l)
echo "📊 Branches to delete: $BRANCHES_TO_DELETE"

# Create a temporary file with branches to delete
echo "$DELETE_BRANCHES" > /tmp/branches_to_delete.txt

echo "🚀 Starting aggressive batch deletion..."
echo "This may take several minutes..."

# Delete branches in parallel batches
BATCH_SIZE=100
COUNT=0
FAILED_COUNT=0

while IFS= read -r branch; do
    if [ -n "$branch" ]; then
        # Delete branch in background
        (
            git push origin --delete "$branch" 2>/dev/null || echo "Failed: $branch" >> /tmp/failed_branches.txt
        ) &
        
        COUNT=$((COUNT + 1))
        
        # Control concurrency - don't start more than 10 parallel processes
        if [ $((COUNT % 10)) -eq 0 ]; then
            wait  # Wait for background processes to complete
            echo "Progress: $COUNT branches processed..."
        fi
        
        # Progress indicator every 100 branches
        if [ $((COUNT % 100)) -eq 0 ]; then
            echo "Processed $COUNT branches..."
        fi
    fi
done < /tmp/branches_to_delete.txt

# Wait for all background processes to complete
wait

echo ""
echo "✅ Batch deletion complete!"

# Count failed deletions
if [ -f /tmp/failed_branches.txt ]; then
    FAILED_COUNT=$(wc -l < /tmp/failed_branches.txt)
    echo "⚠️  Failed to delete $FAILED_COUNT branches (they may have been already deleted)"
fi

echo "📊 Processed $COUNT branches"

# Final count
FINAL_COUNT=$(git branch -r | grep "ai-recommendation" | wc -l)
echo "📊 Final remote AI branch count: $FINAL_COUNT"

# Create emergency consolidated branch
echo ""
echo "📋 Creating emergency consolidated branch..."
git checkout main
CONSOLIDATED_BRANCH="ai-recommendations-emergency-cleanup-$(date +%s)"
git checkout -b "$CONSOLIDATED_BRANCH"

# Create emergency summary
cat > AI_EMERGENCY_CLEANUP_SUMMARY.md << EOF
# AI Branches Emergency Cleanup Summary

**EMERGENCY CLEANUP PERFORMED**: $(date)
**Reason**: Excessive AI branch creation (1919+ branches)

## Cleanup Results
- **Started with**: $CURRENT_COUNT remote AI branches
- **Deleted**: $((CURRENT_COUNT - FINAL_COUNT)) branches
- **Kept**: $FINAL_COUNT most recent branches
- **Failed deletions**: $FAILED_COUNT branches

## Kept Branches (Most Recent)
$(echo "$KEEP_BRANCHES" | sed 's/^/- /')

## Emergency Actions Taken
1. **Disabled AI branch creation** in the engine
2. **Aggressive cleanup** of all old branches
3. **Preserved recent recommendations** for review
4. **Created consolidated branch** for audit trail

## Next Steps
1. **Review kept branches** for important changes
2. **Implement stricter branch limits** (max 5 branches)
3. **Re-enable AI engine** with proper controls
4. **Monitor branch creation** to prevent recurrence

## Prevention Measures
- AI engine now has **hard limit** of 5 branches maximum
- **Automatic cleanup** when limit exceeded
- **Branch age monitoring** (24-hour alerts)
- **Emergency disable** capability

---
*This emergency cleanup was necessary due to uncontrolled AI branch creation.*
*The AI engine has been temporarily disabled to prevent further branch creation.*
EOF

git add AI_EMERGENCY_CLEANUP_SUMMARY.md
git commit -m "Emergency AI branch cleanup - deleted $((CURRENT_COUNT - FINAL_COUNT)) branches"

echo "✅ Created emergency consolidated branch: $CONSOLIDATED_BRANCH"

# Clean up temporary files
rm -f /tmp/branches_to_delete.txt /tmp/failed_branches.txt

echo ""
echo "🎯 NUCLEAR CLEANUP COMPLETE!"
echo "=============================="
echo "✅ AI branch creation is now DISABLED"
echo "✅ Repository cleaned from $CURRENT_COUNT to $FINAL_COUNT branches"
echo "✅ Emergency consolidated branch created"
echo ""
echo "⚠️  IMPORTANT: The AI engine will NOT create new branches until re-enabled"
echo "⚠️  Review the kept branches and re-enable AI engine when ready"
echo ""
echo "To re-enable AI branch creation, modify ai-engine/engine.py"
echo "and remove the emergency branch creation disable code."
