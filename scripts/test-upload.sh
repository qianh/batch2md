#!/bin/bash
# Test upload and conversion workflow

set -e

echo "Testing Batch2MD Web API..."
echo ""

# Create test file
TEST_DIR=$(mktemp -d)
TEST_FILE="$TEST_DIR/test.txt"
echo "This is a test document for conversion." > "$TEST_FILE"
echo "Created test file: $TEST_FILE"
echo ""

# Check if backend is running
echo "Checking if backend is running on port 8000..."
if ! curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "ERROR: Backend is not running on port 8000"
    echo "Please start the backend first: uv run batch2md-web"
    exit 1
fi
echo "✓ Backend is running"
echo ""

# Upload file
echo "Uploading test file..."
UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/api/upload \
    -F "files=@$TEST_FILE")
echo "Upload response: $UPLOAD_RESPONSE"
echo ""

UPLOAD_ID=$(echo $UPLOAD_RESPONSE | grep -o '"upload_id":"[^"]*' | cut -d'"' -f4)
echo "Upload ID: $UPLOAD_ID"
echo ""

# Start conversion
echo "Starting conversion..."
CONVERT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/convert \
    -H "Content-Type: application/json" \
    -d "{
        \"input_path\": \"upload://$UPLOAD_ID\",
        \"recursive\": true,
        \"overwrite\": false,
        \"backend\": \"pipeline\",
        \"timeout\": 300
    }")
echo "Convert response: $CONVERT_RESPONSE"
echo ""

JOB_ID=$(echo $CONVERT_RESPONSE | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)
echo "Job ID: $JOB_ID"
echo ""

# Check status
echo "Checking job status..."
for i in {1..10}; do
    sleep 2
    STATUS_RESPONSE=$(curl -s http://localhost:8000/api/jobs/$JOB_ID)
    echo "Status check $i: $STATUS_RESPONSE"

    STATUS=$(echo $STATUS_RESPONSE | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
        echo ""
        echo "Job $STATUS"
        break
    fi
done

# Cleanup
rm -rf "$TEST_DIR"
echo ""
echo "Test completed. Check backend logs for detailed output."
