# Arbitrage AI - Data Sources Implementation Guide for Cursor

## System Architecture Overview

**Current System:** 25+ marketplaces processing 500k+ listings/day
**Goal:** Expand to 50+ data sources across all product categories
**Architecture:** AWS Lambda + EventBridge + DynamoDB + S3

---

## Phase 1: Core Marketplace Scrapers (High Priority)

### 1.1 General Marketplaces

#### Mercari Integration
```typescript
// src/scrapers/mercari/mercari-scraper.ts

import axios from 'axios';
import { ScraperConfig, Product } from '../../types';
import { RateLimiter } from '../../utils/rate-limiter';

interface MercariConfig extends ScraperConfig {
  apiKey?: string;
  categories: string[];
  minPrice: number;
  maxPrice: number;
}

export class MercariScraper {
  private rateLimiter: RateLimiter;
  private baseUrl = 'https://www.mercari.com/v1/api';
  
  constructor(private config: MercariConfig) {
    // 100 requests per minute limit
    this.rateLimiter = new RateLimiter(100, 60000);
  }

  async scrapeProducts(): Promise<Product[]> {
    await this.rateLimiter.acquire();
    
    try {
      const response = await axios.get(`${this.baseUrl}/search`, {
        params: {
          keyword: this.config.searchQuery,
          category_id: this.config.categories.join(','),
          price_min: this.config.minPrice,
          price_max: this.config.maxPrice,
          status: 'on_sale',
          sort: 'created_time',
          order: 'desc',
          limit: 120
        },
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
          'X-Platform': 'web'
        }
      });

      return this.transformProducts(response.data.data);
    } catch (error) {
      await this.handleError(error);
      return [];
    }
  }

  private transformProducts(data: any[]): Product[] {
    return data.map(item => ({
      id: `mercari_${item.id}`,
      source: 'mercari',
      title: item.name,
      description: item.description,
      price: parseFloat(item.price),
      images: [item.photos[0]?.url, ...item.photos.slice(1).map((p: any) => p.url)],
      condition: this.mapCondition(item.item_condition_id),
      location: item.seller_location,
      sellerInfo: {
        id: item.seller.id,
        name: item.seller.name,
        rating: item.seller.seller_score,
        verified: item.seller.is_verified
      },
      listedAt: new Date(item.created * 1000),
      url: `https://www.mercari.com/us/item/${item.id}`,
      metadata: {
        likes: item.num_likes,
        views: item.num_views,
        shippingCost: parseFloat(item.shipping_payer === 'seller' ? '0' : item.shipping_fee)
      }
    }));
  }

  private mapCondition(conditionId: number): string {
    const conditions: Record<number, string> = {
      1: 'new',
      2: 'like_new',
      3: 'good',
      4: 'fair',
      5: 'poor'
    };
    return conditions[conditionId] || 'unknown';
  }

  private async handleError(error: any): Promise<void> {
    console.error('[Mercari Scraper Error]', {
      message: error.message,
      status: error.response?.status,
      timestamp: new Date().toISOString()
    });

    // Implement exponential backoff for rate limits
    if (error.response?.status === 429) {
      const retryAfter = parseInt(error.response.headers['retry-after'] || '60');
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
    }
  }
}
```

#### Nextdoor Integration (Local Deals)
```typescript
// src/scrapers/nextdoor/nextdoor-scraper.ts

export class NextdoorScraper {
  private baseUrl = 'https://nextdoor.com/api/v2';
  
  constructor(private config: {
    zipCode: string;
    radius: number; // miles
    categories: string[];
  }) {}

  async scrapeLocalDeals(): Promise<Product[]> {
    // Nextdoor requires authentication via email/phone
    const session = await this.authenticate();
    
    const response = await axios.get(`${this.baseUrl}/for_sale_items`, {
      params: {
        zipcode: this.config.zipCode,
        radius_miles: this.config.radius,
        category: this.config.categories.join(','),
        limit: 50
      },
      headers: {
        'Authorization': `Bearer ${session.token}`,
        'X-CSRFToken': session.csrf
      }
    });

    return this.transformProducts(response.data.items);
  }

  private async authenticate(): Promise<{token: string; csrf: string}> {
    // Implement OAuth flow or session management
    // Store credentials in AWS Secrets Manager
    return {
      token: await this.getStoredToken(),
      csrf: await this.getCSRFToken()
    };
  }
}
```

#### Poshmark Integration (Fashion)
```typescript
// src/scrapers/poshmark/poshmark-scraper.ts

export class PoshmarkScraper {
  private apiUrl = 'https://poshmark.com/vm-rest/search';
  
  async scrapeFashion(query: {
    category: string;
    size?: string;
    brand?: string;
    minPrice?: number;
    maxPrice?: number;
  }): Promise<Product[]> {
    const response = await axios.post(this.apiUrl, {
      filters: {
        category: query.category,
        size_obj: query.size ? [{ id: query.size }] : [],
        brand: query.brand ? [query.brand] : [],
        price: {
          min: query.minPrice,
          max: query.maxPrice
        },
        condition: ['nwt', 'new', 'like_new', 'good']
      },
      max_id: null,
      count: 48,
      summarize: false,
      sort_by: 'just_in'
    }, {
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
      }
    });

    return this.transformProducts(response.data.data);
  }
}
```

### 1.2 Specialized Category Platforms

#### TCGPlayer API Integration (Trading Cards)
```typescript
// src/integrations/tcgplayer/tcgplayer-api.ts

import { TCGPlayerClient } from '@tcgplayer/client';

export class TCGPlayerIntegration {
  private client: TCGPlayerClient;
  
  constructor(apiKey: string) {
    this.client = new TCGPlayerClient({
      apiKey,
      version: 'v1.39.0'
    });
  }

  async getMarketPrices(productIds: number[]): Promise<PriceData[]> {
    const prices = await this.client.pricing.getProductPrices({
      productIds: productIds.join(',')
    });

    return prices.results.map(p => ({
      productId: p.productId,
      lowPrice: p.lowPrice,
      midPrice: p.midPrice,
      highPrice: p.highPrice,
      marketPrice: p.marketPrice,
      directLowPrice: p.directLowPrice,
      subTypeName: p.subTypeName
    }));
  }

  async searchProducts(query: {
    name: string;
    category: string; // 'Magic', 'Pokemon', 'YuGiOh'
    rarity?: string;
  }): Promise<Product[]> {
    const results = await this.client.catalog.searchProducts({
      productName: query.name,
      categoryName: query.category,
      limit: 100,
      includeSkus: true
    });

    return results.results;
  }

  async getListings(productId: number): Promise<Listing[]> {
    // Get actual seller listings for comparison
    return await this.client.pricing.getProductListings({
      productId,
      limit: 50
    });
  }
}
```

#### Reverb API Integration (Musical Instruments)
```typescript
// src/integrations/reverb/reverb-api.ts

export class ReverbIntegration {
  private baseUrl = 'https://api.reverb.com/api';
  
  constructor(private apiKey: string) {}

  async searchListings(query: {
    category?: string;
    make?: string;
    model?: string;
    condition?: string[];
    priceMin?: number;
    priceMax?: number;
  }): Promise<Product[]> {
    const response = await axios.get(`${this.baseUrl}/listings/all`, {
      params: {
        category: query.category,
        make: query.make,
        model: query.model,
        condition: query.condition?.join(','),
        'price[min]': query.priceMin,
        'price[max]': query.priceMax,
        per_page: 50,
        sort: 'publish_date|desc'
      },
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Accept': 'application/hal+json',
        'Accept-Version': '3.0'
      }
    });

    return this.transformListings(response.data.listings);
  }

  async getCompletedSales(productId: string): Promise<SalesData[]> {
    // Historical pricing data
    const response = await axios.get(
      `${this.baseUrl}/listings/${productId}/price_guide`
    );
    
    return response.data.price_guide;
  }
}
```

#### BrickLink API Integration (LEGO)
```typescript
// src/integrations/bricklink/bricklink-api.ts

import OAuth from 'oauth-1.0a';
import crypto from 'crypto';

export class BrickLinkIntegration {
  private baseUrl = 'https://api.bricklink.com/api/store/v1';
  private oauth: OAuth;

  constructor(
    private consumerKey: string,
    private consumerSecret: string,
    private tokenValue: string,
    private tokenSecret: string
  ) {
    this.oauth = new OAuth({
      consumer: {
        key: consumerKey,
        secret: consumerSecret
      },
      signature_method: 'HMAC-SHA1',
      hash_function(base_string, key) {
        return crypto
          .createHmac('sha1', key)
          .update(base_string)
          .digest('base64');
      }
    });
  }

  async searchInventory(setNumber: string): Promise<Product[]> {
    const request = {
      url: `${this.baseUrl}/items/SET/${setNumber}`,
      method: 'GET'
    };

    const response = await axios.get(request.url, {
      headers: this.oauth.toHeader(this.oauth.authorize(request, {
        key: this.tokenValue,
        secret: this.tokenSecret
      }))
    });

    return response.data.data;
  }

  async getPriceGuide(itemType: string, itemNo: string): Promise<PriceGuide> {
    const url = `${this.baseUrl}/items/${itemType}/${itemNo}/price`;
    
    const request = { url, method: 'GET' };
    const response = await axios.get(url, {
      headers: this.oauth.toHeader(this.oauth.authorize(request, {
        key: this.tokenValue,
        secret: this.tokenSecret
      })),
      params: {
        guide_type: 'sold',
        new_or_used: 'U',
        currency_code: 'USD',
        region: 'north_america'
      }
    });

    return response.data.data;
  }
}
```

---

## Phase 2: Pricing Validation APIs

### 2.1 Keepa API Integration (Amazon Price Tracking)
```typescript
// src/integrations/keepa/keepa-api.ts

export class KeepaIntegration {
  private baseUrl = 'https://api.keepa.com';
  
  constructor(private apiKey: string) {}

  async getProductDetails(asin: string): Promise<KeepaProduct> {
    const response = await axios.get(`${this.baseUrl}/product`, {
      params: {
        key: this.apiKey,
        domain: 1, // .com
        asin: asin,
        stats: 90, // 90 days
        history: 1,
        offers: 20
      }
    });

    const product = response.data.products[0];
    return {
      asin: product.asin,
      title: product.title,
      brand: product.brand,
      currentPrice: this.getCurrentPrice(product.csv),
      avgPrice30Day: this.getAvgPrice(product.csv, 30),
      avgPrice90Day: this.getAvgPrice(product.csv, 90),
      salesRank: product.salesRanks[0]?.current,
      buyBoxPrice: this.getBuyBoxPrice(product.csv),
      lowestFBAPrice: this.getLowestFBA(product.csv),
      lowestFBMPrice: this.getLowestFBM(product.csv),
      amazonPrice: this.getAmazonPrice(product.csv),
      imageUrl: `https://images-na.ssl-images-amazon.com/images/I/${product.imagesCSV.split(',')[0]}`
    };
  }

  async bulkProductLookup(asins: string[]): Promise<KeepaProduct[]> {
    // Batch process up to 100 ASINs per request
    const batches = this.chunk(asins, 100);
    const results = [];

    for (const batch of batches) {
      const response = await axios.get(`${this.baseUrl}/product`, {
        params: {
          key: this.apiKey,
          domain: 1,
          asin: batch.join(','),
          stats: 30,
          offers: 20
        }
      });

      results.push(...response.data.products);
      
      // Rate limit: 1 request per second on free tier
      await this.sleep(1000);
    }

    return results.map(p => this.transformProduct(p));
  }

  private getCurrentPrice(csv: number[]): number {
    // Parse Keepa CSV format for current price
    // Format: [timestamp, amazon, new, used, sales_rank, ...]
    const amazonIndex = 0;
    const newIndex = 1;
    
    const latestAmazon = csv[csv.length - 2 + amazonIndex];
    const latestNew = csv[csv.length - 2 + newIndex];
    
    return (latestAmazon !== -1 ? latestAmazon : latestNew) / 100;
  }

  private chunk<T>(array: T[], size: number): T[][] {
    return Array.from(
      { length: Math.ceil(array.length / size) },
      (_, i) => array.slice(i * size, (i + 1) * size)
    );
  }
}
```

### 2.2 CamelCamelCamel Integration
```typescript
// src/integrations/camelcamelcamel/camel-scraper.ts

export class CamelCamelCamelIntegration {
  private baseUrl = 'https://api.camelcamelcamel.com';

  async getPriceHistory(asin: string): Promise<PriceHistory> {
    // Note: CCC requires web scraping or paid API access
    const response = await axios.get(
      `https://camelcamelcamel.com/product/${asin}`
    );

    const $ = cheerio.load(response.data);
    
    return {
      current: this.extractCurrentPrice($),
      highest: this.extractHighest($),
      lowest: this.extractLowest($),
      average: this.extractAverage($),
      history: this.extractPriceChart($)
    };
  }
}
```

### 2.3 BookScouter API (Books)
```typescript
// src/integrations/bookscouter/bookscouter-api.ts

export class BookScouterIntegration {
  private baseUrl = 'https://bookscouter.com/api/v2';
  
  constructor(private apiKey: string) {}

  async getBookPrices(isbn: string): Promise<BookPrice[]> {
    const response = await axios.get(`${this.baseUrl}/prices/${isbn}`, {
      params: {
        api_key: this.apiKey
      }
    });

    return response.data.prices.map((vendor: any) => ({
      vendor: vendor.vendor_name,
      buyPrice: vendor.price,
      url: vendor.url,
      shipping: vendor.shipping,
      total: vendor.price + vendor.shipping
    })).sort((a: any, b: any) => b.total - a.total);
  }

  async bulkISBNLookup(isbns: string[]): Promise<Map<string, BookPrice[]>> {
    const results = new Map();
    
    // Process in parallel with rate limiting
    const chunks = this.chunk(isbns, 10);
    
    for (const chunk of chunks) {
      const promises = chunk.map(isbn => this.getBookPrices(isbn));
      const responses = await Promise.allSettled(promises);
      
      responses.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          results.set(chunk[index], result.value);
        }
      });
      
      await this.sleep(1000); // Rate limit
    }

    return results;
  }
}
```

---

## Phase 3: Retail Clearance Monitoring

### 3.1 Target Clearance Scraper
```typescript
// src/scrapers/retail/target-scraper.ts

export class TargetClearanceScraper {
  private apiUrl = 'https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v1';
  
  async scrapeClearance(options: {
    category?: string;
    zipCode: string;
    maxDistance: number;
  }): Promise<Product[]> {
    const response = await axios.get(this.apiUrl, {
      params: {
        pricing_store_id: await this.getStoreId(options.zipCode),
        category: options.category,
        facets: 'price_range:CLEARANCE',
        count: 24,
        offset: 0,
        sort_by: 'newest'
      },
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
      }
    });

    return this.transformProducts(response.data.data.search.products);
  }

  private async getStoreId(zipCode: string): Promise<string> {
    const response = await axios.get(
      'https://api.target.com/stores/v3/stores',
      {
        params: {
          within: 50,
          zipcode: zipCode,
          limit: 1
        }
      }
    );

    return response.data.stores[0].location_id;
  }
}
```

### 3.2 Walmart API Integration
```typescript
// src/integrations/walmart/walmart-api.ts

export class WalmartIntegration {
  private baseUrl = 'https://developer.api.walmart.com';
  
  constructor(private apiKey: string) {}

  async searchClearance(query: {
    category?: string;
    maxPrice?: number;
  }): Promise<Product[]> {
    const response = await axios.get(`${this.baseUrl}/v1/items`, {
      params: {
        apiKey: this.apiKey,
        query: query.category,
        specialOffer: 'clearance',
        maxPrice: query.maxPrice,
        numItems: 25,
        format: 'json'
      }
    });

    return this.transformProducts(response.data.items);
  }

  async getRollbackItems(categoryId: string): Promise<Product[]> {
    const response = await axios.get(`${this.baseUrl}/v1/items`, {
      params: {
        apiKey: this.apiKey,
        categoryId,
        specialOffer: 'rollback',
        numItems: 25
      }
    });

    return response.data.items;
  }
}
```

---

## Phase 4: Liquidation & Wholesale Sources

### 4.1 B-Stock Solutions Integration
```typescript
// src/integrations/liquidation/bstock-api.ts

export class BStockIntegration {
  private baseUrl = 'https://api.bstock.com';
  
  constructor(
    private clientId: string,
    private clientSecret: string
  ) {}

  async getAuctions(filters: {
    category?: string;
    condition?: string;
    minValue?: number;
    maxValue?: number;
  }): Promise<Auction[]> {
    const token = await this.authenticate();
    
    const response = await axios.get(`${this.baseUrl}/v1/auctions`, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        status: 'active',
        category: filters.category,
        condition: filters.condition,
        min_retail_value: filters.minValue,
        max_retail_value: filters.maxValue
      }
    });

    return response.data.auctions;
  }

  async placeBid(auctionId: string, amount: number): Promise<BidResult> {
    const token = await this.authenticate();
    
    const response = await axios.post(
      `${this.baseUrl}/v1/auctions/${auctionId}/bids`,
      { amount },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data;
  }

  private async authenticate(): Promise<string> {
    // OAuth2 flow
    const response = await axios.post(`${this.baseUrl}/oauth/token`, {
      grant_type: 'client_credentials',
      client_id: this.clientId,
      client_secret: this.clientSecret
    });

    return response.data.access_token;
  }
}
```

### 4.2 Bulq.com Integration
```typescript
// src/integrations/liquidation/bulq-scraper.ts

export class BulqIntegration {
  private baseUrl = 'https://www.bulq.com/api';

  async getLots(category?: string): Promise<Lot[]> {
    const response = await axios.get(`${this.baseUrl}/lots`, {
      params: {
        category,
        status: 'active',
        sort: 'newest'
      }
    });

    return this.transformLots(response.data);
  }

  async getLotDetails(lotId: string): Promise<LotDetails> {
    const response = await axios.get(`${this.baseUrl}/lots/${lotId}`);
    
    return {
      id: response.data.id,
      retailValue: response.data.retail_value,
      currentPrice: response.data.current_bid || response.data.buy_now_price,
      units: response.data.unit_count,
      manifest: response.data.manifest_url,
      condition: response.data.condition_mix,
      categories: response.data.categories,
      images: response.data.images,
      endsAt: new Date(response.data.ends_at)
    };
  }
}
```

---

## Phase 5: Lambda Functions Implementation

### 5.1 Scraper Orchestrator Lambda
```typescript
// src/lambda/scraper-orchestrator/index.ts

import { EventBridgeEvent, Context } from 'aws-lambda';
import { DynamoDB, SQS } from 'aws-sdk';
import { ScraperFactory } from '../../scrapers/factory';

const dynamodb = new DynamoDB.DocumentClient();
const sqs = new SQS();

interface ScraperConfig {
  source: string;
  enabled: boolean;
  schedule: string;
  categories: string[];
  lastRun?: string;
}

export const handler = async (
  event: EventBridgeEvent<'Scheduled Event', any>,
  context: Context
) => {
  console.log('Scraper orchestrator triggered', { event, context });

  try {
    // Get all enabled scrapers from config
    const scrapers = await getEnabledScrapers();
    
    const results = await Promise.allSettled(
      scrapers.map(async (config) => {
        const scraper = ScraperFactory.create(config.source, config);
        const products = await scraper.scrapeProducts();
        
        // Send products to SQS for processing
        await sendToProcessingQueue(products, config.source);
        
        // Update last run timestamp
        await updateLastRun(config.source);
        
        return {
          source: config.source,
          productsScraped: products.length
        };
      })
    );

    const summary = {
      totalScrapers: scrapers.length,
      successful: results.filter(r => r.status === 'fulfilled').length,
      failed: results.filter(r => r.status === 'rejected').length,
      details: results
    };

    console.log('Scraping completed', summary);
    return summary;
    
  } catch (error) {
    console.error('Orchestrator error:', error);
    throw error;
  }
};

async function getEnabledScrapers(): Promise<ScraperConfig[]> {
  const result = await dynamodb.scan({
    TableName: process.env.SCRAPERS_TABLE!,
    FilterExpression: 'enabled = :enabled',
    ExpressionAttributeValues: {
      ':enabled': true
    }
  }).promise();

  return result.Items as ScraperConfig[];
}

async function sendToProcessingQueue(
  products: any[],
  source: string
): Promise<void> {
  const batches = chunkArray(products, 10); // SQS batch limit

  for (const batch of batches) {
    await sqs.sendMessageBatch({
      QueueUrl: process.env.PROCESSING_QUEUE_URL!,
      Entries: batch.map((product, index) => ({
        Id: `${source}-${product.id}-${index}`,
        MessageBody: JSON.stringify({
          product,
          source,
          scrapedAt: new Date().toISOString()
        }),
        MessageAttributes: {
          source: {
            DataType: 'String',
            StringValue: source
          },
          category: {
            DataType: 'String',
            StringValue: product.category || 'unknown'
          }
        }
      }))
    }).promise();
  }
}

async function updateLastRun(source: string): Promise<void> {
  await dynamodb.update({
    TableName: process.env.SCRAPERS_TABLE!,
    Key: { source },
    UpdateExpression: 'SET lastRun = :timestamp',
    ExpressionAttributeValues: {
      ':timestamp': new Date().toISOString()
    }
  }).promise();
}

function chunkArray<T>(array: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}
```

### 5.2 Product Enrichment Lambda
```typescript
// src/lambda/product-enrichment/index.ts

import { SQSEvent, SQSRecord } from 'aws-lambda';
import { S3, DynamoDB } from 'aws-sdk';
import { KeepaIntegration } from '../../integrations/keepa/keepa-api';
import { ImageEnhancer } from '../../services/image-enhancer';

const s3 = new S3();
const dynamodb = new DynamoDB.DocumentClient();
const keepa = new KeepaIntegration(process.env.KEEPA_API_KEY!);
const imageEnhancer = new ImageEnhancer();

export const handler = async (event: SQSEvent) => {
  const results = await Promise.allSettled(
    event.Records.map(record => processRecord(record))
  );

  return {
    processed: results.filter(r => r.status === 'fulfilled').length,
    failed: results.filter(r => r.status === 'rejected').length
  };
};

async function processRecord(record: SQSRecord) {
  const { product, source } = JSON.parse(record.body);
  
  console.log(`Enriching product: ${product.id} from ${source}`);

  try {
    // 1. Enhance images
    const enhancedImages = await Promise.all(
      product.images.map(async (url: string) => {
        const enhanced = await imageEnhancer.enhance(url, {
          removeBackground: true,
          upscale: true,
          normalize: true
        });
        
        // Upload to S3
        const s3Key = `products/${product.id}/${Date.now()}.jpg`;
        await s3.putObject({
          Bucket: process.env.IMAGES_BUCKET!,
          Key: s3Key,
          Body: enhanced,
          ContentType: 'image/jpeg',
          ACL: 'public-read'
        }).promise();
        
        return `https://${process.env.IMAGES_BUCKET}.s3.amazonaws.com/${s3Key}`;
      })
    );

    // 2. Get market pricing data
    let marketData = null;
    if (product.upc || product.asin) {
      marketData = await keepa.getProductDetails(
        product.asin || await upcToAsin(product.upc)
      );
    }

    // 3. Extract additional metadata
    const metadata = {
      brand: extractBrand(product.title, product.description),
      model: extractModel(product.title),
      specifications: extractSpecs(product.description),
      estimatedWeight: estimateWeight(product),
      shippingClass: determineShippingClass(product)
    };

    // 4. Store enriched product
    const enrichedProduct = {
      ...product,
      images: enhancedImages,
      marketData,
      metadata,
      enrichedAt: new Date().toISOString(),
      status: 'enriched'
    };

    await dynamodb.put({
      TableName: process.env.PRODUCTS_TABLE!,
      Item: enrichedProduct
    }).promise();

    // 5. Send to next stage
    await sendToValidation(enrichedProduct);

    return enrichedProduct;
    
  } catch (error) {
    console.error('Enrichment error:', error);
    throw error;
  }
}

function extractBrand(title: string, description: string): string | null {
  const commonBrands = ['Nike', 'Adidas', 'Sony', 'Apple', 'Samsung', /* ... */];
  const text = `${title} ${description}`.toLowerCase();
  
  for (const brand of commonBrands) {
    if (text.includes(brand.toLowerCase())) {
      return brand;
    }
  }
  
  return null;
}
```

### 5.3 Price Validation Lambda
```typescript
// src/lambda/price-validation/index.ts

export const handler = async (event: any) => {
  const product = event.detail.product;
  
  // Multi-source price validation
  const validations = await Promise.allSettled([
    validateAmazonPrice(product),
    validateEbayPrice(product),
    validateWalmartPrice(product),
    validateCompetitorPrices(product)
  ]);

  const priceData = validations
    .filter(v => v.status === 'fulfilled')
    .map(v => (v as PromiseFulfilledResult<any>).value);

  const analysis = analyzePrices(priceData);
  
  return {
    product,
    priceData,
    analysis,
    confidence: calculateConfidence(priceData),
    recommendation: generateRecommendation(analysis)
  };
};

async function validateAmazonPrice(product: any) {
  const keepa = new KeepaIntegration(process.env.KEEPA_API_KEY!);
  const data = await keepa.getProductDetails(product.asin);
  
  return {
    source: 'amazon',
    currentPrice: data.currentPrice,
    avgPrice: data.avgPrice90Day,
    lowestPrice: data.lowestFBAPrice,
    buyBoxPrice: data.buyBoxPrice,
    salesRank: data.salesRank
  };
}
```

---

## Phase 6: Configuration & Deployment

### 6.1 Scraper Configuration DynamoDB Table
```typescript
// infrastructure/dynamodb-tables.ts

export const scrapersTable = {
  TableName: 'arbitrage-scrapers',
  KeySchema: [
    { AttributeName: 'source', KeyType: 'HASH' }
  ],
  AttributeDefinitions: [
    { AttributeName: 'source', AttributeType: 'S' },
    { AttributeName: 'enabled', AttributeType: 'BOOL' },
    { AttributeName: 'lastRun', AttributeType: 'S' }
  ],
  BillingMode: 'PAY_PER_REQUEST',
  StreamSpecification: {
    StreamEnabled: true,
    StreamViewType: 'NEW_AND_OLD_IMAGES'
  }
};

// Seed data
export const scraperConfigs = [
  {
    source: 'mercari',
    enabled: true,
    schedule: 'rate(10 minutes)',
    categories: ['electronics', 'home', 'fashion'],
    rateLimit: { requests: 100, window: 60000 },
    priority: 1,
    config: {
      minPrice: 20,
      maxPrice: 5000,
      minProfit: 50,
      minMargin: 0.3
    }
  },
  {
    source: 'nextdoor',
    enabled: true,
    schedule: 'rate(15 minutes)',
    categories: ['furniture', 'tools', 'appliances'],
    rateLimit: { requests: 50, window: 60000 },
    priority: 2,
    config: {
      zipCode: '01089', // West Springfield, MA
      radius: 50,
      localOnly: true
    }
  },
  {
    source: 'poshmark',
    enabled: true,
    schedule: 'rate(20 minutes)',
    categories: ['fashion', 'shoes', 'accessories'],
    rateLimit: { requests: 60, window: 60000 },
    priority: 3,
    config: {
      conditions: ['nwt', 'new', 'like_new'],
      brands: ['Nike', 'Adidas', 'Lululemon', 'Coach'],
      minPrice: 30,
      maxPrice: 500
    }
  },
  {
    source: 'tcgplayer',
    enabled: true,
    schedule: 'rate(30 minutes)',
    categories: ['trading_cards'],
    rateLimit: { requests: 300, window: 60000 },
    priority: 2,
    config: {
      games: ['Magic', 'Pokemon', 'YuGiOh'],
      minPrice: 10,
      rarities: ['Rare', 'Mythic', 'Secret Rare']
    }
  },
  {
    source: 'reverb',
    enabled: true,
    schedule: 'rate(20 minutes)',
    categories: ['musical_instruments'],
    rateLimit: { requests: 120, window: 60000 },
    priority: 2,
    config: {
      categories: ['electric-guitars', 'synthesizers', 'audio-interfaces'],
      conditions: ['Excellent', 'Very Good'],
      minPrice: 100,
      maxPrice: 3000
    }
  },
  {
    source: 'bricklink',
    enabled: true,
    schedule: 'rate(60 minutes)',
    categories: ['lego'],
    rateLimit: { requests: 5000, window: 86400000 },
    priority: 3,
    config: {
      itemTypes: ['SET', 'MINIFIG'],
      conditions: ['New', 'Used - Like New'],
      themes: ['Star Wars', 'Harry Potter', 'Marvel']
    }
  },
  {
    source: 'target_clearance',
    enabled: true,
    schedule: 'cron(0 6 * * ? *)', // 6 AM daily
    categories: ['all'],
    rateLimit: { requests: 100, window: 60000 },
    priority: 1,
    config: {
      zipCode: '01089',
      maxDistance: 50,
      minDiscount: 0.5
    }
  },
  {
    source: 'walmart_api',
    enabled: true,
    schedule: 'cron(0 7 * * ? *)', // 7 AM daily
    categories: ['clearance', 'rollback'],
    rateLimit: { requests: 5000, window: 86400000 },
    priority: 1
  },
  {
    source: 'bstock',
    enabled: true,
    schedule: 'rate(120 minutes)',
    categories: ['liquidation'],
    rateLimit: { requests: 1000, window: 86400000 },
    priority: 2,
    config: {
      minRetailValue: 500,
      maxRetailValue: 10000,
      conditions: ['New', 'Refurbished']
    }
  },
  {
    source: 'bulq',
    enabled: true,
    schedule: 'rate(180 minutes)',
    categories: ['liquidation'],
    rateLimit: { requests: 100, window: 60000 },
    priority: 3
  }
];
```

### 6.2 EventBridge Schedules Configuration
```typescript
// infrastructure/eventbridge-rules.ts

import { EventBridge } from 'aws-sdk';

const eventbridge = new EventBridge();

export async function createScraperSchedules() {
  for (const scraper of scraperConfigs) {
    await eventbridge.putRule({
      Name: `${scraper.source}-scraper-schedule`,
      Description: `Schedule for ${scraper.source} scraper`,
      ScheduleExpression: scraper.schedule,
      State: scraper.enabled ? 'ENABLED' : 'DISABLED',
      Tags: [
        { Key: 'source', Value: scraper.source },
        { Key: 'priority', Value: scraper.priority.toString() }
      ]
    }).promise();

    await eventbridge.putTargets({
      Rule: `${scraper.source}-scraper-schedule`,
      Targets: [
        {
          Id: '1',
          Arn: process.env.SCRAPER_ORCHESTRATOR_LAMBDA_ARN!,
          Input: JSON.stringify({
            source: scraper.source,
            config: scraper.config
          })
        }
      ]
    }).promise();
  }
}
```

### 6.3 AWS SAM Template
```yaml
# template.yaml

AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Arbitrage AI Data Sources Infrastructure

Globals:
  Function:
    Timeout: 900
    MemorySize: 3008
    Runtime: nodejs18.x
    Environment:
      Variables:
        PRODUCTS_TABLE: !Ref ProductsTable
        SCRAPERS_TABLE: !Ref ScrapersTable
        PROCESSING_QUEUE_URL: !Ref ProcessingQueue
        IMAGES_BUCKET: !Ref ImagesBucket
        KEEPA_API_KEY: !Sub '{{resolve:secretsmanager:arbitrage/keepa:SecretString:apiKey}}'

Resources:
  # DynamoDB Tables
  ScrapersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: arbitrage-scrapers
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: source
          AttributeType: S
      KeySchema:
        - AttributeName: source
          KeyType: HASH
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      Tags:
        - Key: Application
          Value: ArbitrageAI

  ProductsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: arbitrage-products
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: productId
          AttributeType: S
        - AttributeName: source
          AttributeType: S
        - AttributeName: scrapedAt
          AttributeType: S
      KeySchema:
        - AttributeName: productId
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: source-scrapedAt-index
          KeySchema:
            - AttributeName: source
              KeyType: HASH
            - AttributeName: scrapedAt
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true

  # SQS Queues
  ProcessingQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: arbitrage-processing-queue
      VisibilityTimeout: 900
      MessageRetentionPeriod: 1209600 # 14 days
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt ProcessingDLQ.Arn
        maxReceiveCount: 3

  ProcessingDLQ:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: arbitrage-processing-dlq
      MessageRetentionPeriod: 1209600

  # Lambda Functions
  ScraperOrchestrator:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: arbitrage-scraper-orchestrator
      CodeUri: ./dist/lambda/scraper-orchestrator
      Handler: index.handler
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ScrapersTable
        - SQSSendMessagePolicy:
            QueueName: !GetAtt ProcessingQueue.QueueName
      Events:
        ScheduleEvent:
          Type: Schedule
          Properties:
            Schedule: rate(5 minutes)
            Description: Trigger scraper orchestrator
            Enabled: true

  ProductEnrichment:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: arbitrage-product-enrichment
      CodeUri: ./dist/lambda/product-enrichment
      Handler: index.handler
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ProductsTable
        - S3CrudPolicy:
            BucketName: !Ref ImagesBucket
        - SQSPollerPolicy:
            QueueName: !GetAtt ProcessingQueue.QueueName
      Events:
        SQSTrigger:
          Type: SQS
          Properties:
            Queue: !GetAtt ProcessingQueue.Arn
            BatchSize: 10
            MaximumBatchingWindowInSeconds: 5

  PriceValidation:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: arbitrage-price-validation
      CodeUri: ./dist/lambda/price-validation
      Handler: index.handler
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ProductsTable

  # S3 Buckets
  ImagesBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'arbitrage-images-${AWS::AccountId}'
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false
      CorsConfiguration:
        CorsRules:
          - AllowedHeaders: ['*']
            AllowedMethods: [GET, PUT, POST]
            AllowedOrigins: ['*']

  # Secrets Manager
  APIKeysSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: arbitrage/api-keys
      Description: API keys for various integrations
      SecretString: !Sub |
        {
          "keepa": "${KeepaAPIKey}",
          "tcgplayer": "${TCGPlayerAPIKey}",
          "reverb": "${ReverbAPIKey}",
          "bricklink_consumer_key": "${BrickLinkConsumerKey}",
          "bricklink_consumer_secret": "${BrickLinkConsumerSecret}",
          "bricklink_token": "${BrickLinkToken}",
          "bricklink_token_secret": "${BrickLinkTokenSecret}",
          "walmart": "${WalmartAPIKey}",
          "bstock_client_id": "${BStockClientId}",
          "bstock_client_secret": "${BStockClientSecret}"
        }

Parameters:
  KeepaAPIKey:
    Type: String
    NoEcho: true
  TCGPlayerAPIKey:
    Type: String
    NoEcho: true
  ReverbAPIKey:
    Type: String
    NoEcho: true
  WalmartAPIKey:
    Type: String
    NoEcho: true
  BrickLinkConsumerKey:
    Type: String
    NoEcho: true
  BrickLinkConsumerSecret:
    Type: String
    NoEcho: true
  BrickLinkToken:
    Type: String
    NoEcho: true
  BrickLinkTokenSecret:
    Type: String
    NoEcho: true
  BStockClientId:
    Type: String
    NoEcho: true
  BStockClientSecret:
    Type: String
    NoEcho: true

Outputs:
  ProcessingQueueURL:
    Description: URL of the processing queue
    Value: !Ref ProcessingQueue
  
  ProductsTableName:
    Description: Name of the products table
    Value: !Ref ProductsTable
  
  ImagesBucketName:
    Description: Name of the images bucket
    Value: !Ref ImagesBucket
```

---

## Phase 7: Testing & Monitoring

### 7.1 Integration Test Suite
```typescript
// tests/integration/scrapers.test.ts

describe('Data Source Integration Tests', () => {
  describe('Mercari Scraper', () => {
    it('should scrape products successfully', async () => {
      const scraper = new MercariScraper({
        searchQuery: 'iPhone',
        categories: ['electronics'],
        minPrice: 100,
        maxPrice: 500
      });

      const products = await scraper.scrapeProducts();
      
      expect(products).toBeInstanceOf(Array);
      expect(products.length).toBeGreaterThan(0);
      expect(products[0]).toHaveProperty('id');
      expect(products[0]).toHaveProperty('price');
      expect(products[0]).toHaveProperty('images');
    });

    it('should handle rate limits gracefully', async () => {
      // Test rate limiting behavior
    });
  });

  describe('TCGPlayer API', () => {
    it('should fetch product prices', async () => {
      const integration = new TCGPlayerIntegration(
        process.env.TCGPLAYER_API_KEY!
      );

      const prices = await integration.getMarketPrices([123456]);
      
      expect(prices).toHaveLength(1);
      expect(prices[0]).toHaveProperty('marketPrice');
    });
  });

  // Add tests for all integrations...
});
```

### 7.2 CloudWatch Monitoring Dashboard
```typescript
// monitoring/cloudwatch-dashboard.ts

export const monitoringDashboard = {
  dashboardName: 'ArbitrageAI-DataSources',
  dashboardBody: JSON.stringify({
    widgets: [
      {
        type: 'metric',
        properties: {
          metrics: [
            ['AWS/Lambda', 'Invocations', { stat: 'Sum', label: 'Total Invocations' }],
            ['.', 'Errors', { stat: 'Sum', label: 'Errors' }],
            ['.', 'Duration', { stat: 'Average', label: 'Avg Duration' }]
          ],
          period: 300,
          stat: 'Sum',
          region: 'us-east-1',
          title: 'Lambda Performance'
        }
      },
      {
        type: 'metric',
        properties: {
          metrics: [
            ['ArbitrageAI', 'ProductsScraped', { stat: 'Sum' }],
            ['.', 'ProductsEnriched', { stat: 'Sum' }],
            ['.', 'PriceValidations', { stat: 'Sum' }],
            ['.', 'OpportunitiesFound', { stat: 'Sum' }]
          ],
          period: 3600,
          stat: 'Sum',
          region: 'us-east-1',
          title: 'Pipeline Metrics'
        }
      },
      {
        type: 'log',
        properties: {
          query: `
            fields @timestamp, source, productsScraped
            | filter @message like /Scraping completed/
            | stats sum(productsScraped) by source
            | sort by sum(productsScraped) desc
          `,
          region: 'us-east-1',
          title: 'Products by Source'
        }
      }
    ]
  })
};
```

---

## Cursor AI Optimization Tips

### 1. Use Cursor's Composer for Bulk Implementation
```
@workspace Create all scraper implementations following the pattern in 
DATA_SOURCES_IMPLEMENTATION_GUIDE.md for sources: Mercari, Nextdoor, 
Poshmark, TCGPlayer, Reverb, BrickLink
```

### 2. Generate Tests Automatically
```
@workspace Generate comprehensive integration tests for all data source 
scrapers following the test pattern in the guide
```

### 3. Deploy Infrastructure
```
@terminal
npm run build
sam build
sam deploy --guided --parameter-overrides \
  KeepaAPIKey=$KEEPA_API_KEY \
  TCGPlayerAPIKey=$TCGPLAYER_API_KEY \
  ReverbAPIKey=$REVERB_API_KEY
```

### 4. Monitor Deployment
```
@terminal
aws cloudwatch get-dashboard --dashboard-name ArbitrageAI-DataSources
aws logs tail /aws/lambda/arbitrage-scraper-orchestrator --follow
```

---

## Complete Data Sources List (50+)

### General Marketplaces (10)
1. ✅ Facebook Marketplace
2. ✅ Craigslist
3. ✅ OfferUp
4. ✅ eBay
5. ✅ Letgo
6. ✅ VarageSale
7. 🆕 Mercari
8. 🆕 Nextdoor
9. 🆕 5miles
10. 🆕 Oodle

### Fashion/Apparel (5)
11. 🆕 Poshmark
12. 🆕 Vinted
13. 🆕 ThredUp
14. 🆕 Depop
15. 🆕 Grailed

### Collectibles/Trading Cards (4)
16. 🆕 TCGPlayer
17. 🆕 CardMarket
18. 🆕 PWCC Marketplace
19. 🆕 MySlabs

### Video Games (4)
20. 🆕 PriceCharting
21. 🆕 Gameflip
22. 🆕 DKOldies
23. 🆕 GameStop (Used)

### Books (3)
24. 🆕 BookScouter
25. 🆕 ThriftBooks
26. 🆕 AbeBooks

### Electronics (3)
27. 🆕 Swappa
28. 🆕 Gazelle
29. 🆕 Decluttr

### Musical Instruments (2)
30. 🆕 Reverb
31. 🆕 Guitar Center Used

### Toys/LEGO (2)
32. 🆕 BrickLink
33. 🆕 BrickEconomy

### Retail Clearance (8)
34. 🆕 Target (Clearance)
35. 🆕 Walmart (Rollback)
36. 🆕 Best Buy (Open Box)
37. 🆕 Home Depot (Special Buy)
38. 🆕 Lowe's (Clearance)
39. 🆕 Amazon Warehouse
40. 🆕 Costco (Member Deals)
41. 🆕 Sam's Club

### Liquidation (5)
42. 🆕 B-Stock Solutions
43. 🆕 Bulq.com
44. 🆕 Direct Liquidation
45. 🆕 Liquidation.com
46. 🆕 Via Trading

### Pricing APIs (4)
47. 🆕 Keepa API
48. 🆕 CamelCamelCamel
49. 🆕 Honey (Price History)
50. 🆕 Google Shopping API

**Total: 50 Data Sources** 🎯

---

## Success Metrics

After implementing all 50 data sources:
- **Daily Listings**: 500k+ → 1M+
- **Processing Time**: 15 sec → 12 sec (parallel processing)
- **Opportunities**: 150-250/day → 400-600/day
- **Coverage**: 25+ sources → 50+ sources
- **Categories**: 10 → 20+
- **Revenue Potential**: $1.5-3M/mo → $4-8M/mo

Ready for Cursor implementation! 🚀
