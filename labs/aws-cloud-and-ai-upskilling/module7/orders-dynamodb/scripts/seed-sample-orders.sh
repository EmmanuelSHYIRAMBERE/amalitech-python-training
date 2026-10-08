#!/usr/bin/env bash
# Seeds a handful of sample orders into the given environment's Orders
# table, for manual console verification (view/insert/query) per the
# lab's rubric. Run from CloudShell or any shell with AWS CLI configured
# against the target account/region.
#
# Usage: ./seed-sample-orders.sh dev
#        ./seed-sample-orders.sh prod
set -euo pipefail

ENVIRONMENT="${1:?Usage: $0 <dev|prod>}"
TABLE_NAME="emmanuel-orders-${ENVIRONMENT}"

put_order() {
  local order_id="$1" created_at="$2" customer_id="$3" status="$4" total="$5" region="$6"
  aws dynamodb put-item \
    --table-name "$TABLE_NAME" \
    --item "{
      \"orderId\": {\"S\": \"${order_id}\"},
      \"createdAt\": {\"S\": \"${created_at}\"},
      \"customerId\": {\"S\": \"${customer_id}\"},
      \"status\": {\"S\": \"${status}\"},
      \"totalAmount\": {\"N\": \"${total}\"},
      \"region\": {\"S\": \"${region}\"}
    }"
}

echo "Seeding sample orders into ${TABLE_NAME}..."

put_order "ord-1001" "2026-10-01T09:00:00Z" "cust-alice" "PENDING"  "89.99"  "eu-north-1"
put_order "ord-1002" "2026-10-01T10:30:00Z" "cust-alice" "SHIPPED"  "45.50"  "eu-north-1"
put_order "ord-1003" "2026-10-02T14:15:00Z" "cust-bob"   "PENDING"  "120.00" "eu-west-1"

echo "Done. Verify with:"
echo "  aws dynamodb scan --table-name ${TABLE_NAME}"
echo "  aws dynamodb query --table-name ${TABLE_NAME} --index-name CustomerOrdersIndex --key-condition-expression 'customerId = :c' --expression-attribute-values '{\":c\":{\"S\":\"cust-alice\"}}'"
echo "  aws dynamodb query --table-name ${TABLE_NAME} --index-name StatusOrdersIndex --key-condition-expression '#s = :s' --expression-attribute-names '{\"#s\":\"status\"}' --expression-attribute-values '{\":s\":{\"S\":\"PENDING\"}}'"
