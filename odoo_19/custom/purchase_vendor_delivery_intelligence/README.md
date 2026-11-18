# Purchase Vendor Delivery Intelligence

## Overview

Purchase Vendor Delivery Intelligence helps monitor supplier delivery performance and identify purchase order delivery risks.

It provides:

- Frozen supplier delivery promises
- Supplier delivery reliability scoring
- Purchase line delivery metrics
- Delivery risk levels
- Risk alerts and activities
- Vendor delivery intelligence reports

## Features

- Track original supplier delivery promises
- Measure delivery performance using receipt data
- Calculate on-time delivery and fill-rate metrics
- Identify critical, at-risk, and due-soon purchase lines
- Maintain company-specific delivery configuration
- Refresh delivery intelligence manually or through scheduled actions

## Dependencies

This module depends on:

- `purchase_stock`
- `mail`

## Configuration

Delivery intelligence thresholds can be configured from the Purchase settings.

## Security

The module uses standard Odoo access groups and company-aware data handling.

## Performance and Data Refresh

The module is designed to avoid per-line receipt queries during delivery intelligence refresh.

- Receipt evidence is collected in batch for purchase order lines.
- Delivery metrics are refreshed through ORM-based batch processing.
- The daily scheduled action refreshes confirmed and completed purchase orders for the current company.
- Manual recalculation is also available from purchase orders.
- Stored delivery metrics are refreshed when the intelligence refresh is triggered.
- Date-driven risk evaluation uses the original supplier promise, grace period, and current delivery status.

For large datasets, batch processing and ORM prefetching are preferred over repeated per-line database queries.

## Design Rationale

The module extends standard Odoo Purchase and Stock models using inheritance instead of modifying Odoo core code.

The delivery promise is captured as a frozen baseline so that later supplier-date changes can be compared against the original commitment.

Company-specific configuration is used so delivery scoring and risk thresholds remain isolated between companies.

The module uses standard Odoo ORM operations and access groups and does not rely on hard-coded database IDs or direct database access.

The implementation is intended to remain generic for supplier delivery monitoring and to support future OCA-style maintenance and review.

## Testing

The module includes tests covering:

- Delivery intelligence calculations
- Security
- Company isolation
- Receipt evidence
- Frozen supplier promise baseline
- Scheduled refresh behavior

## License

AGPL-3