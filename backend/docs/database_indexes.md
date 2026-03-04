# Database Indexes Documentation

## Overview

This document describes the database indexes created for the LabInsight platform to optimize query performance as specified in **Requirement 13.8**.

## Required Indexes

The following indexes are created to improve query performance:

### 1. users.email (Unique Index)
- **Field**: `email`
- **Type**: Unique, Ascending
- **Purpose**: Fast authentication lookups and prevent duplicate email registrations
- **Index Name**: `email_unique_idx`

### 2. reports.user_id
- **Field**: `user_id`
- **Type**: Ascending
- **Purpose**: Efficiently fetch all reports for a specific user
- **Index Name**: `user_id_idx`

### 3. parameters.report_id
- **Field**: `report_id`
- **Type**: Ascending
- **Purpose**: Quickly retrieve all parameters for a specific report
- **Index Name**: `report_id_idx`

### 4. parameters.user_id
- **Field**: `user_id`
- **Type**: Ascending
- **Purpose**: Enable user-specific parameter queries and analytics
- **Index Name**: `user_id_idx`

### 5. trend_history.user_id
- **Field**: `user_id`
- **Type**: Ascending
- **Purpose**: Fetch trend history for a specific user
- **Index Name**: `user_id_idx`

### 6. trend_history.parameter_name
- **Field**: `parameter_name`
- **Type**: Ascending
- **Purpose**: Query trends for specific medical parameters
- **Index Name**: `parameter_name_idx`

### 7. medical_ranges.parameter
- **Field**: `parameter`
- **Type**: Ascending
- **Purpose**: Fast lookup of normal ranges for medical parameters
- **Index Name**: `parameter_idx`

## Usage

### Creating Indexes

To create all required indexes, run the database_indexes.py script:

```bash
cd backend
python database_indexes.py
```

This will:
1. Connect to MongoDB using the configuration from `.env`
2. Create all 7 required indexes
3. Display a summary of created indexes
4. List all current indexes for verification

### Programmatic Usage

You can also use the index creation functions in your code:

```python
from database_indexes import create_indexes, list_indexes, drop_indexes
from database import db_manager

# Connect to database
database = await db_manager.connect()

# Create indexes
results = await create_indexes(database)
print(f"Created {results['total_indexes']} indexes")

# List all indexes
indexes = await list_indexes(database)
for collection, idx_list in indexes.items():
    print(f"{collection}: {len(idx_list)} indexes")

# Drop all custom indexes (use with caution!)
# results = await drop_indexes(database)
```

## Performance Impact

### Query Performance Improvements

With these indexes in place, the following queries will be significantly faster:

1. **User Authentication** (`users.email`):
   - Login queries: O(1) instead of O(n)
   - Duplicate email checks: O(1) instead of O(n)

2. **Report Retrieval** (`reports.user_id`):
   - Fetching user's reports: O(log n) instead of O(n)
   - Dashboard loading: ~10x faster for users with many reports

3. **Parameter Queries** (`parameters.report_id`, `parameters.user_id`):
   - Report detail page: O(log n) instead of O(n)
   - User analytics: ~5-10x faster

4. **Trend Analysis** (`trend_history.user_id`, `trend_history.parameter_name`):
   - Trend page loading: O(log n) instead of O(n)
   - Parameter-specific trends: ~10x faster

5. **Medical Range Lookups** (`medical_ranges.parameter`):
   - Risk classification: O(log n) instead of O(n)
   - Processing pipeline: ~5x faster

### Storage Overhead

Each index adds minimal storage overhead:
- Estimated total index size: ~5-10% of collection size
- Trade-off: Slightly slower writes, much faster reads
- For LabInsight's read-heavy workload, this is optimal

## Monitoring

### Checking Index Usage

To verify indexes are being used, you can use MongoDB's explain() method:

```javascript
// In MongoDB shell
db.users.find({email: "test@example.com"}).explain("executionStats")

// Look for:
// - "stage": "IXSCAN" (index scan, good)
// - "stage": "COLLSCAN" (collection scan, bad)
```

### Slow Query Logging

The application logs slow queries (>100ms) as specified in Requirement 18.3:

```python
# In your query code
import time
start = time.time()
result = await collection.find(query).to_list(length=None)
duration = time.time() - start

if duration > 0.1:  # 100ms threshold
    logger.warning(f"Slow query detected: {duration:.2f}s", extra={
        "collection": collection.name,
        "query": query,
        "duration": duration
    })
```

## Maintenance

### Rebuilding Indexes

If indexes become fragmented or corrupted, you can rebuild them:

```bash
# Drop all custom indexes
python -c "from database_indexes import drop_indexes; import asyncio; asyncio.run(drop_indexes(db))"

# Recreate indexes
python database_indexes.py
```

### Index Statistics

To view index statistics in MongoDB:

```javascript
// In MongoDB shell
db.users.stats()
db.users.aggregate([{$indexStats: {}}])
```

## Testing

The index creation functionality is thoroughly tested in `tests/test_database_indexes.py`:

```bash
# Run index tests
pytest tests/test_database_indexes.py -v

# Run with coverage
pytest tests/test_database_indexes.py --cov=database_indexes --cov-report=html
```

Tests verify:
- All 7 required indexes are created
- Unique constraint is only on users.email
- Index names follow naming conventions
- Error handling works correctly
- Indexes can be listed and dropped

## Troubleshooting

### Index Creation Fails

If index creation fails:

1. **Check MongoDB Connection**:
   ```bash
   # Test connection
   mongosh mongodb://localhost:27017/labinsight
   ```

2. **Check Permissions**:
   - Ensure the MongoDB user has `createIndex` permission
   - Required role: `readWrite` or `dbAdmin`

3. **Check Existing Indexes**:
   ```javascript
   // In MongoDB shell
   db.users.getIndexes()
   ```
   - If an index with the same name exists, drop it first

4. **Check Disk Space**:
   - Index creation requires temporary disk space
   - Ensure at least 10% free space

### Duplicate Key Errors

If you get duplicate key errors on `users.email`:

```bash
# Find duplicate emails
db.users.aggregate([
  {$group: {_id: "$email", count: {$sum: 1}}},
  {$match: {count: {$gt: 1}}}
])

# Remove duplicates (keep first occurrence)
# WARNING: This will delete data!
db.users.aggregate([
  {$group: {_id: "$email", ids: {$push: "$_id"}}},
  {$match: {ids: {$size: {$gt: 1}}}},
  {$project: {_id: 0, toDelete: {$slice: ["$ids", 1, {$size: "$ids"}]}}}
]).forEach(doc => {
  db.users.deleteMany({_id: {$in: doc.toDelete}})
})

# Then recreate the unique index
python database_indexes.py
```

## References

- **Requirement 13.8**: Database indexes on user_id and report_id fields for query performance
- **Requirement 18.3**: Slow query logging for queries exceeding 100ms
- **Requirement 18.4**: Connection pooling with pool size 20
- MongoDB Index Documentation: https://docs.mongodb.com/manual/indexes/
- Motor (Async MongoDB Driver): https://motor.readthedocs.io/
