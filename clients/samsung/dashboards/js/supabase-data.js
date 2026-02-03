/**
 * Samsung AI Visibility Dashboard - Supabase Data Service
 *
 * Reusable module for fetching data from Supabase.
 * Provides RPC functions and data transformations for dashboard components.
 */

// ============================================
// SUPABASE CONFIGURATION
// ============================================
const SupabaseConfig = {
    url: 'https://zozzhptqoclvbfysmopg.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvenpocHRxb2NsdmJmeXNtb3BnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwNzA2NzksImV4cCI6MjA4NDY0NjY3OX0.3Q9gv49xrtqdmlesJgYDMVYUwjldy45xZw7O-nkASus'
};

// ============================================
// BRAND COLORS (from design tokens)
// ============================================
const BrandColors = {
    samsung: '#1428A0',
    lg: '#A50034',
    sony: '#000000',
    tcl: '#E31937',
    hisense: '#00A0DF',
    xbox: '#107C10',
    roku: '#6C3C97',
    other: '#9e9e9e'
};

// Map brand names to colors (case-insensitive lookup)
function getBrandColor(brandName) {
    if (!brandName) return BrandColors.other;
    const key = brandName.toLowerCase().replace(/\s+/g, '');
    return BrandColors[key] || BrandColors.other;
}

// ============================================
// ACCENT COLORS (for charts)
// ============================================
const AccentColors = {
    blue: '#0277c6',
    cyan: '#02b2e4',
    teal: '#01c3b0',
    purple: '#8091df',
    green: '#96d551',
    yellow: '#feb447',
    red: '#ff4438'
};

// ============================================
// SEMANTIC COLORS
// ============================================
const SemanticColors = {
    success: '#4caf50',
    error: '#f44336',
    neutral: '#9e9e9e',
    positive: '#96d551',
    negative: '#ff4438'
};

// ============================================
// MODEL CONFIGURATION
// ============================================
const ModelConfig = {
    labels: {
        'search-gpt': 'ChatGPT',
        'google-ai-overview': 'Google AI Overview',
        'google-ai-mode': 'Google AI Mode',
        'perplexity': 'Perplexity',
        'claude': 'Claude',
        'copilot': 'Copilot',
        'gemini': 'Gemini'
    },
    colors: {
        'search-gpt': '#01c3b0',
        'google-ai-overview': '#0277c6',
        'google-ai-mode': '#feb447',
        'perplexity': '#22c55e',
        'claude': '#d97706',
        'copilot': '#0ea5e9',
        'gemini': '#8b5cf6'
    }
};

function getModelLabel(modelId) {
    return ModelConfig.labels[modelId] || modelId;
}

function getModelColor(modelId) {
    return ModelConfig.colors[modelId] || AccentColors.purple;
}

// ============================================
// SUPABASE API HELPERS
// ============================================

/**
 * Make a direct REST API query to Supabase
 * @param {string} endpoint - Table name
 * @param {object} params - Query parameters
 * @returns {Promise<Array>} - Query results
 */
async function supabaseQuery(endpoint, params = {}) {
    const url = new URL(`${SupabaseConfig.url}/rest/v1/${endpoint}`);
    Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
            url.searchParams.append(key, value);
        }
    });

    const response = await fetch(url, {
        headers: {
            'apikey': SupabaseConfig.anonKey,
            'Authorization': `Bearer ${SupabaseConfig.anonKey}`
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Supabase query error: ${response.status} - ${errorText}`);
    }

    return response.json();
}

/**
 * Call a Supabase RPC function
 * @param {string} functionName - RPC function name
 * @param {object} params - Function parameters
 * @returns {Promise<any>} - RPC result
 */
async function callRPC(functionName, params = {}) {
    const response = await fetch(`${SupabaseConfig.url}/rest/v1/rpc/${functionName}`, {
        method: 'POST',
        headers: {
            'apikey': SupabaseConfig.anonKey,
            'Authorization': `Bearer ${SupabaseConfig.anonKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Supabase RPC error: ${response.status} - ${errorText}`);
    }

    return response.json();
}

// ============================================
// DATE HELPERS
// ============================================

/**
 * Convert a days-ago value to an ISO date string
 * @param {string|number} days - Number of days or 'all'
 * @returns {string|null} - ISO date string or null for all time
 */
function getDateFilter(days) {
    if (days === 'all' || days === null || days === undefined) return null;
    const date = new Date();
    date.setDate(date.getDate() - parseInt(days));
    return date.toISOString().split('T')[0];
}

/**
 * Format a date for display
 * @param {string} dateStr - ISO date string
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} - Formatted date string
 */
function formatDate(dateStr, options = { month: 'short', day: 'numeric' }) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', options);
}

// ============================================
// DATA FETCHING FUNCTIONS
// ============================================

/**
 * Fetch daily mentions aggregated by date/model/brand
 * Uses the get_daily_mentions RPC function
 * @param {string|null} dateFrom - Start date filter (ISO format)
 * @param {string} model - Model filter ('all' or specific model)
 * @returns {Promise<Array>} - Aggregated mention data
 */
async function fetchDailyMentions(dateFrom = null, model = 'all') {
    const params = {
        date_from: dateFrom,
        model_filter: model === 'all' ? null : model
    };
    return callRPC('get_daily_mentions', params);
}

/**
 * Fetch top concept categories with sentiment breakdown
 * Uses the get_top_categories RPC function
 * @param {string|null} dateFrom - Start date filter
 * @param {string} model - Model filter
 * @param {number} limit - Max number of categories
 * @returns {Promise<Array>} - Category data with sentiment
 */
async function fetchTopCategories(dateFrom = null, model = 'all', limit = 10) {
    const params = {
        date_from: dateFrom,
        model_filter: model === 'all' ? null : model,
        limit_count: limit
    };
    return callRPC('get_top_categories', params);
}

/**
 * Fetch concept mentions data with optional filters
 * @param {object} filters - Query filters
 * @returns {Promise<Array>} - Concept mention records
 */
async function fetchConceptMentions(filters = {}) {
    const params = {
        select: '*',
        order: 'date.desc,mentions.desc'
    };

    if (filters.dateFrom) {
        params['date'] = `gte.${filters.dateFrom}`;
    }
    if (filters.brand) {
        params['brand'] = `eq.${filters.brand}`;
    }
    if (filters.model) {
        params['model'] = `eq.${filters.model}`;
    }
    if (filters.limit) {
        params['limit'] = filters.limit;
    }

    return supabaseQuery('semrush_concept_mentions', params);
}

/**
 * Fetch cited pages data
 * @param {object} filters - Query filters
 * @returns {Promise<Array>} - Cited page records
 */
async function fetchCitedPages(filters = {}) {
    const params = {
        select: '*',
        order: 'prompts_count.desc'
    };

    if (filters.domain) {
        params['domain'] = `eq.${filters.domain}`;
    }
    if (filters.domainLike) {
        params['domain'] = `ilike.%${filters.domainLike}%`;
    }
    if (filters.limit) {
        params['limit'] = filters.limit;
    }

    return supabaseQuery('semrush_cited_pages', params);
}

/**
 * Fetch URL prompts data
 * @param {object} filters - Query filters
 * @returns {Promise<Array>} - URL prompt records
 */
async function fetchUrlPrompts(filters = {}) {
    const params = {
        select: '*',
        order: 'volume.desc'
    };

    if (filters.topic) {
        params['topic'] = `eq.${filters.topic}`;
    }
    if (filters.llm) {
        params['llm'] = `eq.${filters.llm}`;
    }
    if (filters.limit) {
        params['limit'] = filters.limit;
    }

    return supabaseQuery('semrush_url_prompts', params);
}

// ============================================
// KPI CALCULATIONS
// ============================================

/**
 * Calculate dashboard KPIs from daily mentions data
 * @param {Array} data - Daily mentions data (aggregated by date/model/brand)
 * @returns {object} - Calculated KPI values
 */
function calculateKPIs(data) {
    const brandMentions = {};
    const modelMentions = {};
    let totalMentions = 0;
    let totalPositive = 0;
    let totalNegative = 0;
    let totalNeutral = 0;

    data.forEach(row => {
        const brand = row.brand || 'Other';
        const model = row.model || 'unknown';

        if (!brandMentions[brand]) {
            brandMentions[brand] = 0;
        }
        brandMentions[brand] += row.total_mentions || 0;

        if (!modelMentions[model]) {
            modelMentions[model] = 0;
        }
        modelMentions[model] += row.total_mentions || 0;

        totalMentions += row.total_mentions || 0;
        totalPositive += row.sentiment_positive || 0;
        totalNegative += row.sentiment_negative || 0;
        totalNeutral += row.sentiment_neutral || 0;
    });

    const samsungMentions = brandMentions['Samsung'] || 0;
    const shareOfVoice = totalMentions > 0 ? (samsungMentions / totalMentions * 100) : 0;

    // Visibility score (normalized 0-100)
    const visibilityScore = totalMentions > 0
        ? Math.min(100, (samsungMentions / totalMentions * 100) * 1.5)
        : 0;

    // Sentiment score (net sentiment as percentage)
    const totalSentiment = totalPositive + totalNegative + totalNeutral;
    const sentimentScore = totalSentiment > 0
        ? ((totalPositive - totalNegative) / totalSentiment * 100)
        : 0;

    return {
        shareOfVoice: shareOfVoice.toFixed(1),
        visibilityScore: Math.round(visibilityScore),
        sentimentScore: sentimentScore >= 0 ? `+${sentimentScore.toFixed(0)}` : sentimentScore.toFixed(0),
        totalMentions: samsungMentions,
        totalMentionsFormatted: samsungMentions.toLocaleString(),
        brandMentions,
        modelMentions,
        sentiment: {
            positive: totalPositive,
            negative: totalNegative,
            neutral: totalNeutral
        }
    };
}

/**
 * Calculate source visibility metrics from cited pages data
 * @param {Array} data - Cited pages data
 * @returns {object} - Source visibility metrics
 */
function calculateSourceVisibility(data) {
    let samsungCitations = 0;
    let totalCitations = 0;
    let samsungUrls = 0;
    let totalUrls = data.length;

    const sourceTypes = {
        owned: { count: 0, citations: 0 },
        earned: { count: 0, citations: 0 },
        social: { count: 0, citations: 0 },
        competitor: { count: 0, citations: 0 },
        other: { count: 0, citations: 0 }
    };

    const socialDomains = ['reddit.com', 'twitter.com', 'x.com', 'facebook.com', 'youtube.com'];
    const competitorDomains = ['lg.com', 'sony.com', 'tcl.com', 'hisense.com'];

    data.forEach(row => {
        const citations = row.prompts_count || 0;
        totalCitations += citations;

        const domain = (row.domain || '').toLowerCase();

        // Classify source type
        if (domain.includes('samsung.com')) {
            sourceTypes.owned.count++;
            sourceTypes.owned.citations += citations;
            samsungCitations += citations;
            samsungUrls++;
        } else if (socialDomains.some(s => domain.includes(s))) {
            sourceTypes.social.count++;
            sourceTypes.social.citations += citations;
        } else if (competitorDomains.some(c => domain.includes(c))) {
            sourceTypes.competitor.count++;
            sourceTypes.competitor.citations += citations;
        } else if (domain) {
            sourceTypes.earned.count++;
            sourceTypes.earned.citations += citations;
        } else {
            sourceTypes.other.count++;
            sourceTypes.other.citations += citations;
        }
    });

    const visibility = totalCitations > 0
        ? (samsungCitations / totalCitations * 100).toFixed(1)
        : 0;

    return {
        visibility,
        samsungCitations,
        samsungUrls,
        totalCitations,
        totalUrls,
        sourceTypes
    };
}

// ============================================
// DATA TRANSFORMATIONS FOR CHARTS
// ============================================

/**
 * Transform daily mentions data for brand trend line chart
 * @param {Array} data - Daily mentions data
 * @param {Array} brands - Brands to include (default: top 5 TV brands)
 * @returns {object} - Data formatted for D3 line chart
 */
function transformForBrandTrendChart(data, brands = ['Samsung', 'LG', 'Sony', 'TCL', 'Hisense']) {
    // Group by date and brand
    const dateMap = new Map();

    data.forEach(row => {
        if (!brands.includes(row.brand)) return;

        const date = row.date;
        if (!dateMap.has(date)) {
            dateMap.set(date, {});
        }
        const dayData = dateMap.get(date);
        dayData[row.brand] = (dayData[row.brand] || 0) + (row.total_mentions || 0);
    });

    // Convert to array sorted by date
    const dates = Array.from(dateMap.keys()).sort();
    const series = brands.map(brand => ({
        name: brand,
        color: getBrandColor(brand),
        values: dates.map(date => ({
            date,
            value: dateMap.get(date)[brand] || 0
        }))
    }));

    return { dates, series };
}

/**
 * Transform concept mentions for sunburst chart hierarchy
 * @param {Array} data - Concept mentions data
 * @returns {object} - Hierarchical data for D3 sunburst
 */
function transformForSunburst(data) {
    const categories = new Map();

    data.forEach(row => {
        const cat = row.concept_category || 'Other';
        const subcat = row.concept_subcategory || 'General';
        const concept = row.concept || 'Unknown';
        const mentions = row.mentions || 0;

        if (!categories.has(cat)) {
            categories.set(cat, new Map());
        }
        const catMap = categories.get(cat);

        if (!catMap.has(subcat)) {
            catMap.set(subcat, []);
        }
        catMap.get(subcat).push({
            name: concept,
            value: mentions,
            sentiment: {
                positive: row.sentiment_positive || 0,
                negative: row.sentiment_negative || 0,
                neutral: row.sentiment_neutral || 0
            }
        });
    });

    // Build hierarchy
    const children = [];
    categories.forEach((subcats, catName) => {
        const catChildren = [];
        subcats.forEach((concepts, subcatName) => {
            catChildren.push({
                name: subcatName,
                children: concepts
            });
        });
        children.push({
            name: catName,
            children: catChildren
        });
    });

    return {
        name: 'root',
        children
    };
}

/**
 * Transform data for heatmap (brand x concept matrix)
 * @param {Array} data - Concept mentions data
 * @param {number} conceptLimit - Max concepts to include
 * @returns {object} - Heatmap data with brands, concepts, and values
 */
function transformForHeatmap(data, conceptLimit = 20) {
    const brands = ['Samsung', 'LG', 'Sony', 'TCL', 'Hisense'];
    const conceptMap = new Map();

    // Aggregate mentions by concept and brand
    data.forEach(row => {
        const concept = row.concept || 'Unknown';
        const brand = row.brand || 'Other';
        const mentions = row.mentions || 0;

        if (!conceptMap.has(concept)) {
            conceptMap.set(concept, { total: 0, brands: {} });
        }
        const entry = conceptMap.get(concept);
        entry.total += mentions;
        entry.brands[brand] = (entry.brands[brand] || 0) + mentions;
    });

    // Get top concepts by total mentions
    const topConcepts = Array.from(conceptMap.entries())
        .sort((a, b) => b[1].total - a[1].total)
        .slice(0, conceptLimit)
        .map(([name]) => name);

    // Build matrix
    const matrix = topConcepts.map(concept => {
        const entry = conceptMap.get(concept);
        return {
            concept,
            values: brands.map(brand => ({
                brand,
                value: entry.brands[brand] || 0
            }))
        };
    });

    // Find max value for color scaling
    const maxValue = Math.max(...matrix.flatMap(row => row.values.map(v => v.value)));

    return { brands, concepts: topConcepts, matrix, maxValue };
}

/**
 * Transform data for treemap (concepts sized by mentions, colored by sentiment)
 * @param {Array} data - Concept mentions data
 * @param {string} brand - Filter by brand (default: Samsung)
 * @returns {object} - Hierarchical data for D3 treemap
 */
function transformForTreemap(data, brand = 'Samsung') {
    const filtered = data.filter(row => row.brand === brand);
    const conceptMap = new Map();

    filtered.forEach(row => {
        const concept = row.concept || 'Unknown';
        if (!conceptMap.has(concept)) {
            conceptMap.set(concept, {
                mentions: 0,
                positive: 0,
                negative: 0,
                neutral: 0
            });
        }
        const entry = conceptMap.get(concept);
        entry.mentions += row.mentions || 0;
        entry.positive += row.sentiment_positive || 0;
        entry.negative += row.sentiment_negative || 0;
        entry.neutral += row.sentiment_neutral || 0;
    });

    const children = Array.from(conceptMap.entries()).map(([name, stats]) => {
        const total = stats.positive + stats.negative + stats.neutral;
        const sentimentScore = total > 0
            ? (stats.positive - stats.negative) / total
            : 0;

        return {
            name,
            value: stats.mentions,
            sentiment: sentimentScore,
            stats
        };
    });

    return {
        name: brand,
        children: children.sort((a, b) => b.value - a.value)
    };
}

/**
 * Transform data for radar chart (model performance comparison)
 * @param {Array} data - Daily mentions data
 * @returns {object} - Radar chart data
 */
function transformForRadar(data) {
    const models = ['search-gpt', 'google-ai-overview', 'google-ai-mode'];
    const metrics = ['Total Mentions', 'Positive Sentiment', 'Unique Concepts', 'Top Position Rate'];

    const modelStats = {};
    models.forEach(model => {
        modelStats[model] = {
            totalMentions: 0,
            positiveSentiment: 0,
            totalSentiment: 0,
            concepts: new Set(),
            topPositions: 0,
            totalPositions: 0
        };
    });

    data.forEach(row => {
        const model = row.model;
        if (!modelStats[model]) return;

        const stats = modelStats[model];
        stats.totalMentions += row.total_mentions || 0;
        stats.positiveSentiment += row.sentiment_positive || 0;
        stats.totalSentiment += (row.sentiment_positive || 0) + (row.sentiment_negative || 0) + (row.sentiment_neutral || 0);

        if (row.concept) {
            stats.concepts.add(row.concept);
        }
    });

    // Normalize metrics to 0-100 scale
    const maxMentions = Math.max(...Object.values(modelStats).map(s => s.totalMentions));
    const maxConcepts = Math.max(...Object.values(modelStats).map(s => s.concepts.size));

    const radarData = models.map(model => {
        const stats = modelStats[model];
        const posRate = stats.totalSentiment > 0
            ? (stats.positiveSentiment / stats.totalSentiment * 100)
            : 0;

        return {
            model,
            label: getModelLabel(model),
            color: getModelColor(model),
            values: [
                maxMentions > 0 ? (stats.totalMentions / maxMentions * 100) : 0,
                posRate,
                maxConcepts > 0 ? (stats.concepts.size / maxConcepts * 100) : 0,
                50 // Placeholder for top position rate - needs actual position data
            ]
        };
    });

    return { metrics, data: radarData };
}

/**
 * Transform data for Sankey diagram (topic -> prompt -> URL flow)
 * @param {Array} promptData - URL prompts data
 * @param {Array} citedData - Cited pages data
 * @returns {object} - Sankey nodes and links
 */
function transformForSankey(promptData, citedData) {
    const nodes = [];
    const links = [];
    const nodeIndex = new Map();

    // Get unique topics
    const topics = [...new Set(promptData.map(p => p.topic).filter(Boolean))].slice(0, 10);
    topics.forEach(topic => {
        nodeIndex.set(`topic:${topic}`, nodes.length);
        nodes.push({ name: topic, type: 'topic' });
    });

    // Get unique prompts (limited)
    const prompts = promptData.slice(0, 20);
    prompts.forEach(p => {
        if (!p.prompt) return;
        const promptKey = `prompt:${p.prompt}`;
        if (!nodeIndex.has(promptKey)) {
            nodeIndex.set(promptKey, nodes.length);
            nodes.push({ name: p.prompt.substring(0, 50), type: 'prompt' });
        }

        // Link topic -> prompt
        const topicKey = `topic:${p.topic}`;
        if (nodeIndex.has(topicKey)) {
            links.push({
                source: nodeIndex.get(topicKey),
                target: nodeIndex.get(promptKey),
                value: p.volume || 1
            });
        }
    });

    // Get unique URLs from cited pages (limited)
    const urls = citedData.slice(0, 15);
    urls.forEach(u => {
        if (!u.url) return;
        const urlKey = `url:${u.url}`;
        if (!nodeIndex.has(urlKey)) {
            nodeIndex.set(urlKey, nodes.length);
            const isSamsung = (u.domain || '').includes('samsung');
            nodes.push({
                name: u.url.substring(0, 40),
                type: 'url',
                isSamsung
            });
        }
    });

    return { nodes, links };
}

// ============================================
// EXPORT (for use in dashboard)
// ============================================
window.SupabaseData = {
    // Configuration
    config: SupabaseConfig,
    colors: {
        brand: BrandColors,
        accent: AccentColors,
        semantic: SemanticColors,
        getBrandColor,
        getModelColor,
        getModelLabel
    },

    // API helpers
    query: supabaseQuery,
    rpc: callRPC,

    // Date helpers
    getDateFilter,
    formatDate,

    // Data fetching
    fetchDailyMentions,
    fetchTopCategories,
    fetchConceptMentions,
    fetchCitedPages,
    fetchUrlPrompts,

    // KPI calculations
    calculateKPIs,
    calculateSourceVisibility,

    // Data transformations
    transform: {
        brandTrendChart: transformForBrandTrendChart,
        sunburst: transformForSunburst,
        heatmap: transformForHeatmap,
        treemap: transformForTreemap,
        radar: transformForRadar,
        sankey: transformForSankey
    }
};
