# Production-Ready React/Vite Stripe Payment System on Google Cloud Run

This comprehensive guide provides everything needed to build and deploy a production-ready payment system for collecting $500 non-refundable website deposits using React/Vite, Stripe, and Google Cloud Run.

## Stripe Integration with React/Vite

The modern approach uses Stripe's Payment Element, supporting 40+ payment methods with a single integration. **Initialize your Vite project** with TypeScript for better type safety, then install the required dependencies: `@stripe/react-stripe-js`, `@stripe/stripe-js`, and `axios`. The Payment Element automatically handles security, validation, and error handling, making it superior to older integration methods.

Your **environment configuration** requires careful separation of keys. Use the `VITE_` prefix for frontend variables in Vite projects, storing publishable keys in `.env` files while keeping secret keys exclusively on the backend. For the $500 fixed deposit, create a payment intent on your backend that includes proper metadata marking it as non-refundable.

The **React component architecture** centers around a CheckoutForm wrapped in Stripe's Elements provider. The form should prominently display the $500 amount with clear "non-refundable deposit" messaging. Implement progressive disclosure for terms, requiring explicit consent via checkbox before payment submission. The Payment Element handles all card validation and 3D Secure authentication automatically.

```javascript
// Core payment intent creation (backend)
const paymentIntent = await stripe.paymentIntents.create({
  amount: 50000, // $500 in cents
  currency: "usd",
  automatic_payment_methods: { enabled: true },
  description: "Non-refundable deposit - $500",
  metadata: {
    type: "deposit",
    refundable: "false"
  }
});
```

## Secure Backend Implementation with Node.js/Express

The backend requires **comprehensive security middleware** including helmet for headers, express-rate-limit for DDoS protection, and proper CORS configuration. Implement payment-specific rate limiting allowing only 5 payment attempts per 15 minutes per IP address. This prevents abuse while maintaining legitimate user access.

Your **payment processing endpoints** must validate all inputs using Joi schemas, sanitize data to prevent XSS attacks, and handle errors gracefully without exposing sensitive information. Create separate endpoints for payment intent creation and webhook handling, with raw body parsing only for the webhook endpoint to maintain signature verification integrity.

**Error handling** requires a sophisticated approach distinguishing between card errors, rate limits, and processing failures. Implement exponential backoff retry logic for transient errors while immediately rejecting permanent failures like declined cards. Provide customer-friendly error messages with actionable suggestions rather than technical error codes.

## Stripe Webhook Configuration

**Webhook security** is critical for payment confirmation. Verify signatures using Stripe's SDK with the webhook secret from your dashboard. Implement idempotency to prevent duplicate processing by tracking event IDs. Handle the primary events: `payment_intent.succeeded` for successful payments and `payment_intent.payment_failed` for failures.

For **payment confirmation**, trigger email receipts, database updates, and business logic fulfillment only after successful webhook verification. Store minimal payment data locally - just the Stripe payment ID, amount, status, and timestamp. Let Stripe handle all sensitive card data storage.

**Webhook resilience** requires proper HTTP status codes (always return 200 for received events), timeout handling, and graceful degradation. Implement a dead letter queue for failed processing attempts and monitor webhook health through Stripe's dashboard.

## Google Cloud Secret Manager Integration

**Secret Manager setup** begins with creating a dedicated service account with minimal permissions - only `secretmanager.secretAccessor` and `run.invoker` roles. Store Stripe API keys, webhook secrets, and database credentials as versioned secrets, implementing automatic rotation schedules for enhanced security.

Access secrets **programmatically** using the Node.js client library with caching to minimize API calls and costs. Implement a 5-minute cache timeout and batch secret retrieval when multiple secrets are needed. Never log secret values, even in development environments.

For **production deployment**, grant your Cloud Run service account access to specific secrets rather than project-wide permissions. Use secret versioning to support zero-downtime key rotation, maintaining both current and backup Stripe instances during transitions.

## Docker Containerization Strategy

The **multi-stage Dockerfile** optimizes both build time and image size. First stage builds the React/Vite frontend, second stage prepares the Node.js backend, and the final stage combines both using Alpine Linux for minimal attack surface. Always run as a non-root user (UID 1001) and expose only port 8080.

**Security hardening** includes using specific version tags instead of `latest`, implementing health checks, and properly handling environment variables. The `.dockerignore` file must exclude all sensitive files, development dependencies, and build artifacts. Final image size should be under 150MB for optimal Cloud Run performance.

For **local development**, use Docker Compose with separate services for frontend, backend, and database. Mount volumes for hot reloading but exclude node_modules to prevent conflicts. This setup mirrors production architecture while maintaining development efficiency.

## Google Cloud Run Production Configuration

**Service configuration** for payment processing requires specific optimizations: 2 CPU cores, 2GB memory, minimum 1 instance to prevent cold starts, maximum 100 instances for scalability, and 10 concurrent requests per instance to prevent payment processing conflicts. Disable CPU throttling for consistent performance.

Deploy using **generation 2 execution environment** for better cold start performance. Set request timeout to 300 seconds to accommodate slow payment authorizations. Configure autoscaling based on CPU utilization rather than request count for more predictable performance.

**Regional deployment** should prioritize `us-central1` for lowest latency to Stripe's infrastructure. For global applications, deploy to multiple regions behind a Global Load Balancer. Consider data residency requirements - EU customers may require `europe-west1` deployment for GDPR compliance.

## HTTPS and Custom Domain Setup

The **recommended approach** uses Google Cloud Load Balancer with managed SSL certificates. This provides automatic certificate renewal, global anycast IP addresses, and built-in DDoS protection. Configure the load balancer with a serverless NEG (Network Endpoint Group) pointing to your Cloud Run service.

**SSL certificates** should use Google-managed certificates for automatic provisioning and renewal. Initial provisioning takes 15 minutes to 24 hours. Configure CAA records in your DNS to authorize Google's certificate authority. Always redirect HTTP to HTTPS at the load balancer level.

For **DNS configuration**, create A records pointing to the load balancer's IP address. Use Cloud CDN for static assets to reduce origin requests and costs. Implement security headers including HSTS with a one-year max-age and CSP policies allowing Stripe's domains.

## Database Selection for Payment Records

**Cloud SQL PostgreSQL is strongly recommended** for payment processing over Firestore due to ACID compliance, complex query support, mature ecosystem, and easier regulatory compliance. Payment data requires strict consistency and complex reporting queries that NoSQL databases struggle with.

Configure Cloud SQL with **high availability** using regional configuration, automatic failover, and point-in-time recovery. Enable daily backups with 30-day retention. Use connection pooling with 20 maximum connections to handle Cloud Run's concurrent request model efficiently.

The **payment schema** should include separate tables for transactions, audit logs, and payment methods. Index on user_id, status, and created_at for query performance. Store amounts as DECIMAL(10,2) to avoid floating-point precision issues. Include JSONB columns for flexible gateway response storage.

## Non-Refundable Deposit Legal Framework

**Legal compliance** requires deposits to function as liquidated damages, not penalties. The $500 amount must reasonably estimate actual losses from cancellation including setup costs, opportunity costs, and reserved capacity. Document these justifications in your terms of service.

**Terms must clearly state** the deposit is non-refundable upon project commencement, define specific commencement milestones, explain refund exceptions (company non-performance), and specify how deposits apply to final invoices. Include dispute resolution procedures favoring arbitration over litigation.

For **GDPR compliance**, obtain explicit consent for data processing, provide clear privacy policies, honor data subject rights regardless of deposit status, and sign Data Processing Agreements with Stripe. CCPA requires additional disclosures for California residents including "Do Not Sell" options.

## Payment Testing Strategy

**Test mode configuration** uses Stripe's test API keys and specific test card numbers. Use `4242424242424242` for successful payments, `4000000000003220` for 3D Secure authentication, and various decline codes for failure scenarios. Test webhook events using Stripe CLI forwarding to localhost.

The **testing checklist** covers payment form rendering, amount display accuracy, validation messages, loading states, success redirects, mobile responsiveness, webhook signature verification, email delivery, and database updates. Test both happy paths and every possible failure scenario.

**Stripe CLI** enables local webhook testing without internet exposure. Install via Homebrew or direct download, authenticate with `stripe login`, then forward events using `stripe listen --forward-to localhost:3000/webhook`. Trigger specific events with `stripe trigger payment_intent.succeeded`.

## Error Handling and Failure Scenarios

Implement **comprehensive error classification** distinguishing between card errors (user-facing messages), rate limit errors (retry guidance), network errors (automatic retry), and validation errors (field-specific feedback). Never expose internal error details or stack traces to users.

**Retry mechanisms** should use exponential backoff starting at 1 second, doubling up to 10 seconds maximum. Don't retry permanent failures like card declines or authentication failures. Log all retry attempts with correlation IDs for debugging.

For **payment failures**, automatically notify customers via email with specific decline reasons and resolution steps. Provide self-service retry links valid for 24 hours. Track failure patterns to identify potential fraud or system issues requiring intervention.

## CI/CD Pipeline with GitHub Actions

The **deployment pipeline** includes automated testing, security scanning, container building, and Cloud Run deployment. Use workload identity federation for keyless authentication. Implement separate workflows for production (main branch) and staging (pull requests).

**Environment management** uses Terraform modules for infrastructure as code. Separate configurations for development, staging, and production environments. Store environment-specific variables in Google Secret Manager rather than GitHub secrets for better security.

**Monitoring setup** includes custom Cloud Monitoring dashboards tracking request rates, error rates, payment success rates, and latency percentiles. Configure alerts for high error rates (>5% over 5 minutes), database connection exhaustion, and monthly cost thresholds.

## Production Security Checklist

**Critical security measures** include TLS 1.2+ enforcement, OWASP security headers via Helmet, input validation on all endpoints, SQL injection prevention through parameterized queries, XSS protection through output encoding, and CSRF protection using SameSite cookies.

**PCI compliance** even with Stripe requires using hosted payment fields (never touching raw card data), maintaining secure development practices, completing annual SAQ-A assessments, implementing proper network segmentation, and maintaining audit logs for all payment activities.

**Audit logging** must capture all payment attempts, webhook events, and administrative actions. Store logs in Google Cloud Logging with 90-day retention. Never log sensitive data like full card numbers, CVV codes, or API keys. Include correlation IDs for transaction tracing.

## Performance Optimization

**Cold start mitigation** requires maintaining minimum instances, using generation 2 execution environment, optimizing container size under 150MB, implementing health check endpoints, and pre-warming critical code paths. Monitor cold start frequency and adjust minimum instances accordingly.

**Resource optimization** involves right-sizing CPU and memory based on metrics, implementing response caching where appropriate, using connection pooling for databases, enabling gzip compression, and serving static assets via CDN. Monitor resource utilization weekly and adjust allocations.

**Cost management** strategies include setting budget alerts at 50%, 80%, and 90% thresholds, using committed use discounts for predictable workloads, implementing request coalescing where possible, regularly reviewing and removing unused resources, and optimizing database queries to reduce compute time.

This production-ready implementation provides enterprise-grade payment processing with comprehensive security, scalability for growth, and full regulatory compliance. Regular security audits, performance monitoring, and cost optimization ensure long-term sustainability of your payment infrastructure.