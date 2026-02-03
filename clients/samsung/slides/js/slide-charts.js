/**
 * Samsung TV Panel Type Slides - Chart Rendering
 * D3.js-based charts for donut, treemap, and radar visualizations
 */

// Brand colors
const BRAND_COLORS = {
    'Samsung': '#1428A0',
    'LG': '#A50034',
    'Sony': '#000000',
    'TCL': '#E31937',
    'Hisense': '#00A0DF'
};

// AI Model colors
const MODEL_COLORS = {
    'google-ai-mode': '#feb447',
    'google-ai-overview': '#0277c6',
    'chatgpt': '#01c3b0'
};

// Model display names
const MODEL_NAMES = {
    'google-ai-mode': 'Google AI Mode',
    'google-ai-overview': 'Google AI Overview',
    'chatgpt': 'ChatGPT'
};

// Sentiment colors
const SENTIMENT_COLORS = {
    'positive': '#96d551',
    'neutral': '#9e9e9e',
    'negative': '#ff4438'
};

/**
 * Render a donut chart for platform distribution
 * @param {string} containerId - DOM element ID
 * @param {Array} data - Array of {model, prompts, citations}
 * @param {string} centerLabel - Optional label for center text (default: 'citations tracked')
 */
function renderDonut(containerId, data, centerLabel = 'citations tracked') {
    const container = document.getElementById(containerId);
    const width = container.clientWidth;
    const height = container.clientHeight - 40; // Reserve space for legend below
    const radius = Math.min(width, height) / 2 - 10;

    // Clear existing
    d3.select(`#${containerId}`).selectAll('*').remove();

    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${width / 2}, ${height / 2})`);

    const total = d3.sum(data, d => d.citations);

    const pie = d3.pie()
        .value(d => d.citations)
        .sort(null);

    const arc = d3.arc()
        .innerRadius(radius * 0.6)
        .outerRadius(radius);

    const arcs = svg.selectAll('arc')
        .data(pie(data))
        .enter()
        .append('g');

    arcs.append('path')
        .attr('d', arc)
        .attr('fill', d => MODEL_COLORS[d.data.model] || '#ccc')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d) {
            d3.select(this).attr('opacity', 0.8);
            tooltip.style('display', 'block')
                .html(`<strong>${MODEL_NAMES[d.data.model]}</strong><br/>
                       ${d.data.citations.toLocaleString()} citations<br/>
                       ${((d.data.citations / total) * 100).toFixed(1)}%`);
        })
        .on('mousemove', function(event) {
            tooltip.style('left', (event.pageX + 10) + 'px')
                   .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseout', function() {
            d3.select(this).attr('opacity', 1);
            tooltip.style('display', 'none');
        });

    // Center text
    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '-0.2em')
        .style('font-family', 'Samsung Sharp Sans, sans-serif')
        .style('font-size', '28px')
        .style('font-weight', '700')
        .text(total.toLocaleString());

    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '1.2em')
        .style('font-family', 'Samsung One, sans-serif')
        .style('font-size', '12px')
        .style('fill', '#666')
        .text(centerLabel);

    // Legend - positioned below the chart SVG (not absolute)
    const legend = d3.select(`#${containerId}`)
        .append('div')
        .attr('class', 'chart-legend')
        .style('display', 'flex')
        .style('justify-content', 'center')
        .style('flex-wrap', 'wrap')
        .style('gap', '12px')
        .style('margin-top', '8px')
        .style('padding', '0 8px');

    data.forEach(d => {
        const item = legend.append('div')
            .style('display', 'flex')
            .style('align-items', 'center')
            .style('gap', '6px');

        item.append('div')
            .style('width', '12px')
            .style('height', '12px')
            .style('border-radius', '2px')
            .style('background', MODEL_COLORS[d.model]);

        item.append('span')
            .style('font-size', '10px')
            .style('color', '#666')
            .text(`${MODEL_NAMES[d.model]} (${((d.citations / total) * 100).toFixed(0)}%)`);
    });
}

/**
 * Render a treemap for concepts & sentiment
 * @param {string} containerId - DOM element ID
 * @param {Array} data - Array of {concept, sentiment, mentions}
 */
function renderTreemap(containerId, data) {
    const container = document.getElementById(containerId);
    const width = container.clientWidth;
    const height = container.clientHeight - 30; // Reserve space for legend

    // Clear existing
    d3.select(`#${containerId}`).selectAll('*').remove();

    // Aggregate by concept (combine sentiments)
    const conceptMap = new Map();
    data.forEach(d => {
        if (!conceptMap.has(d.concept)) {
            conceptMap.set(d.concept, { concept: d.concept, mentions: 0, sentiments: {} });
        }
        const entry = conceptMap.get(d.concept);
        entry.mentions += d.mentions;
        entry.sentiments[d.sentiment] = (entry.sentiments[d.sentiment] || 0) + d.mentions;
    });

    const concepts = Array.from(conceptMap.values())
        .sort((a, b) => b.mentions - a.mentions)
        .slice(0, 15);

    // Determine dominant sentiment for color
    concepts.forEach(c => {
        const total = c.mentions;
        const positive = c.sentiments.positive || 0;
        const negative = c.sentiments.negative || 0;
        const neutral = c.sentiments.neutral || 0;

        if (positive >= negative && positive >= neutral) {
            c.dominantSentiment = 'positive';
            c.sentimentRatio = positive / total;
        } else if (negative >= positive && negative >= neutral) {
            c.dominantSentiment = 'negative';
            c.sentimentRatio = negative / total;
        } else {
            c.dominantSentiment = 'neutral';
            c.sentimentRatio = neutral / total;
        }
    });

    const root = d3.hierarchy({ children: concepts })
        .sum(d => d.mentions);

    d3.treemap()
        .size([width, height])
        .padding(2)
        (root);

    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const nodes = svg.selectAll('g')
        .data(root.leaves())
        .enter()
        .append('g')
        .attr('transform', d => `translate(${d.x0},${d.y0})`);

    nodes.append('rect')
        .attr('width', d => d.x1 - d.x0)
        .attr('height', d => d.y1 - d.y0)
        .attr('fill', d => {
            const color = SENTIMENT_COLORS[d.data.dominantSentiment];
            // Adjust opacity based on sentiment ratio
            return d3.color(color).copy({opacity: 0.6 + d.data.sentimentRatio * 0.4});
        })
        .attr('stroke', '#fff')
        .attr('stroke-width', 1)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d) {
            d3.select(this).attr('stroke', '#333').attr('stroke-width', 2);
            const pos = d.data.sentiments.positive || 0;
            const neu = d.data.sentiments.neutral || 0;
            const neg = d.data.sentiments.negative || 0;
            tooltip.style('display', 'block')
                .html(`<strong>${d.data.concept}</strong><br/>
                       ${d.data.mentions.toLocaleString()} mentions<br/>
                       <span style="color:#96d551">+${pos}</span> /
                       <span style="color:#9e9e9e">${neu}</span> /
                       <span style="color:#ff4438">-${neg}</span>`);
        })
        .on('mousemove', function(event) {
            tooltip.style('left', (event.pageX + 10) + 'px')
                   .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseout', function() {
            d3.select(this).attr('stroke', '#fff').attr('stroke-width', 1);
            tooltip.style('display', 'none');
        });

    // Concept name labels (only for cells large enough)
    nodes.append('text')
        .attr('x', 4)
        .attr('y', 14)
        .style('font-family', 'Samsung One, sans-serif')
        .style('font-size', d => {
            const w = d.x1 - d.x0;
            const h = d.y1 - d.y0;
            return (w > 60 && h > 30) ? '13px' : '10px';
        })
        .style('fill', d => d.data.dominantSentiment === 'neutral' ? '#333' : '#fff')
        .style('pointer-events', 'none')
        .text(d => {
            const w = d.x1 - d.x0;
            const h = d.y1 - d.y0;
            if (w < 40 || h < 22) return '';
            const label = d.data.concept;
            const maxChars = Math.floor(w / 5.5);
            return label.length > maxChars ? label.slice(0, maxChars - 2) + '...' : label;
        });

    // Mention count labels (only for large cells > 80px wide, > 40px tall)
    nodes.append('text')
        .attr('x', 4)
        .attr('y', 28)
        .style('font-family', 'Samsung One, sans-serif')
        .style('font-size', '10px')
        .style('fill', d => d.data.dominantSentiment === 'neutral' ? '#555' : 'rgba(255,255,255,0.85)')
        .style('pointer-events', 'none')
        .text(d => {
            const w = d.x1 - d.x0;
            const h = d.y1 - d.y0;
            if (w < 80 || h < 40) return '';
            return d.data.mentions.toLocaleString();
        });

    // Sentiment color legend below treemap
    const legend = d3.select(`#${containerId}`)
        .append('div')
        .style('display', 'flex')
        .style('justify-content', 'center')
        .style('gap', '16px')
        .style('margin-top', '8px')
        .style('font-family', 'Samsung One, sans-serif')
        .style('font-size', '11px');

    const sentimentLabels = [
        { key: 'positive', label: 'Positive' },
        { key: 'neutral', label: 'Neutral' },
        { key: 'negative', label: 'Negative' }
    ];

    sentimentLabels.forEach(s => {
        const item = legend.append('div')
            .style('display', 'flex')
            .style('align-items', 'center')
            .style('gap', '4px');

        item.append('div')
            .style('width', '12px')
            .style('height', '12px')
            .style('border-radius', '2px')
            .style('background', SENTIMENT_COLORS[s.key]);

        item.append('span')
            .style('color', '#666')
            .text(s.label);
    });
}

/**
 * Render a horizontal bar chart for competitor comparison
 * @param {string} containerId - DOM element ID
 * @param {Array} data - Array of {brand_name, mentions, unique_concepts, positive_pct}
 */
function renderCompetitorBars(containerId, data) {
    const container = document.getElementById(containerId);
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Clear existing
    d3.select(`#${containerId}`).selectAll('*').remove();

    // Sort by mentions descending and take top 5
    const sortedData = data.slice().sort((a, b) => b.mentions - a.mentions).slice(0, 5);
    const maxMentions = d3.max(sortedData, d => d.mentions);

    // Chart dimensions
    const margin = { top: 10, right: 10, bottom: 10, left: 70 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    const barHeight = Math.min(36, (chartHeight - 40) / sortedData.length);
    const barGap = 8;

    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const chart = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Create bars
    sortedData.forEach((d, i) => {
        const y = i * (barHeight + barGap) + 10;
        const barWidth = (d.mentions / maxMentions) * (chartWidth - 120);
        const brandColor = BRAND_COLORS[d.brand_name] || '#666';
        const isSamsung = d.brand_name === 'Samsung';

        // Brand name label
        chart.append('text')
            .attr('x', -8)
            .attr('y', y + barHeight / 2)
            .attr('text-anchor', 'end')
            .attr('dominant-baseline', 'middle')
            .style('font-family', 'Samsung One, sans-serif')
            .style('font-size', '12px')
            .style('font-weight', isSamsung ? '700' : '400')
            .style('fill', brandColor)
            .text(d.brand_name);

        // Background bar (track)
        chart.append('rect')
            .attr('x', 0)
            .attr('y', y)
            .attr('width', chartWidth - 120)
            .attr('height', barHeight)
            .attr('fill', '#f0f0f0')
            .attr('rx', 4);

        // Value bar
        chart.append('rect')
            .attr('x', 0)
            .attr('y', y)
            .attr('width', barWidth)
            .attr('height', barHeight)
            .attr('fill', brandColor)
            .attr('opacity', isSamsung ? 1 : 0.75)
            .attr('rx', 4);

        // Mention count and sentiment breakdown label
        const positivePct = parseFloat(d.positive_pct) || 0;
        const negativePct = parseFloat(d.negative_pct) || 0;
        const neutralPct = Math.max(0, 100 - positivePct - negativePct);

        chart.append('text')
            .attr('x', chartWidth - 115)
            .attr('y', y + barHeight / 2)
            .attr('dominant-baseline', 'middle')
            .style('font-family', 'Samsung One, sans-serif')
            .style('font-size', '11px')
            .style('font-weight', isSamsung ? '600' : '400')
            .style('fill', '#333')
            .text(`${d.mentions.toLocaleString()}`);

        // Sentiment breakdown with color-coded percentages
        const sentimentText = chart.append('text')
            .attr('x', chartWidth - 50)
            .attr('y', y + barHeight / 2)
            .attr('dominant-baseline', 'middle')
            .style('font-family', 'Samsung One, sans-serif')
            .style('font-size', '9px');

        sentimentText.append('tspan').attr('fill', '#96d551').text(`${positivePct.toFixed(0)}%`);
        sentimentText.append('tspan').attr('fill', '#666').text(' / ');
        sentimentText.append('tspan').attr('fill', '#9e9e9e').text(`${neutralPct.toFixed(0)}%`);
        sentimentText.append('tspan').attr('fill', '#666').text(' / ');
        sentimentText.append('tspan').attr('fill', '#ff4438').text(`${negativePct.toFixed(0)}%`);
    });
}

// Alias for backwards compatibility
const renderRadar = renderCompetitorBars;

/**
 * Render horizontal stacked bar chart for concepts with sentiment breakdown
 * @param {string} containerId - DOM element ID
 * @param {Array} data - Array of {concept, sentiment, mentions}
 */
function renderConceptBars(containerId, data) {
    const container = document.getElementById(containerId);
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Clear existing
    d3.select(`#${containerId}`).selectAll('*').remove();

    // Aggregate by concept (combine sentiments)
    const conceptMap = new Map();
    data.forEach(d => {
        if (!conceptMap.has(d.concept)) {
            conceptMap.set(d.concept, { concept: d.concept, positive: 0, neutral: 0, negative: 0, total: 0 });
        }
        const entry = conceptMap.get(d.concept);
        entry[d.sentiment] = (entry[d.sentiment] || 0) + d.mentions;
        entry.total += d.mentions;
    });

    const concepts = Array.from(conceptMap.values())
        .sort((a, b) => b.total - a.total)
        .slice(0, 10);

    // Chart dimensions - wider left margin for full concept names
    const margin = { top: 10, right: 60, bottom: 20, left: 180 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    const barHeight = Math.min(28, (chartHeight - 20) / concepts.length);
    const barGap = 4;

    const maxTotal = d3.max(concepts, d => d.total);

    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const chart = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Create stacked bars for each concept
    concepts.forEach((d, i) => {
        const y = i * (barHeight + barGap);
        const barWidth = (d.total / maxTotal) * chartWidth;

        // Calculate segment widths
        const posWidth = (d.positive / d.total) * barWidth;
        const neuWidth = (d.neutral / d.total) * barWidth;
        const negWidth = (d.negative / d.total) * barWidth;

        // Concept label - full name, no truncation
        chart.append('text')
            .attr('x', -8)
            .attr('y', y + barHeight / 2)
            .attr('text-anchor', 'end')
            .attr('dominant-baseline', 'middle')
            .style('font-family', 'Samsung One, sans-serif')
            .style('font-size', '11px')
            .style('fill', '#333')
            .text(d.concept);

        // Background track
        chart.append('rect')
            .attr('x', 0)
            .attr('y', y)
            .attr('width', chartWidth)
            .attr('height', barHeight)
            .attr('fill', '#f0f0f0')
            .attr('rx', 4);

        // Positive segment (green)
        let xOffset = 0;
        if (d.positive > 0) {
            chart.append('rect')
                .attr('x', xOffset)
                .attr('y', y)
                .attr('width', posWidth)
                .attr('height', barHeight)
                .attr('fill', SENTIMENT_COLORS.positive)
                .attr('rx', xOffset === 0 ? 4 : 0)
                .style('cursor', 'pointer')
                .on('mouseover', function(event) {
                    tooltip.style('display', 'block')
                        .html(`<strong>${d.concept}</strong><br/>
                               <span style="color:#96d551">Positive: ${d.positive.toLocaleString()}</span><br/>
                               ${((d.positive / d.total) * 100).toFixed(1)}% of mentions`);
                })
                .on('mousemove', function(event) {
                    tooltip.style('left', (event.pageX + 10) + 'px')
                           .style('top', (event.pageY - 10) + 'px');
                })
                .on('mouseout', function() {
                    tooltip.style('display', 'none');
                });
            xOffset += posWidth;
        }

        // Neutral segment (gray)
        if (d.neutral > 0) {
            chart.append('rect')
                .attr('x', xOffset)
                .attr('y', y)
                .attr('width', neuWidth)
                .attr('height', barHeight)
                .attr('fill', SENTIMENT_COLORS.neutral)
                .style('cursor', 'pointer')
                .on('mouseover', function(event) {
                    tooltip.style('display', 'block')
                        .html(`<strong>${d.concept}</strong><br/>
                               <span style="color:#9e9e9e">Neutral: ${d.neutral.toLocaleString()}</span><br/>
                               ${((d.neutral / d.total) * 100).toFixed(1)}% of mentions`);
                })
                .on('mousemove', function(event) {
                    tooltip.style('left', (event.pageX + 10) + 'px')
                           .style('top', (event.pageY - 10) + 'px');
                })
                .on('mouseout', function() {
                    tooltip.style('display', 'none');
                });
            xOffset += neuWidth;
        }

        // Negative segment (red)
        if (d.negative > 0) {
            chart.append('rect')
                .attr('x', xOffset)
                .attr('y', y)
                .attr('width', negWidth)
                .attr('height', barHeight)
                .attr('fill', SENTIMENT_COLORS.negative)
                .attr('rx', xOffset + negWidth >= barWidth - 1 ? 4 : 0)
                .style('cursor', 'pointer')
                .on('mouseover', function(event) {
                    tooltip.style('display', 'block')
                        .html(`<strong>${d.concept}</strong><br/>
                               <span style="color:#ff4438">Negative: ${d.negative.toLocaleString()}</span><br/>
                               ${((d.negative / d.total) * 100).toFixed(1)}% of mentions`);
                })
                .on('mousemove', function(event) {
                    tooltip.style('left', (event.pageX + 10) + 'px')
                           .style('top', (event.pageY - 10) + 'px');
                })
                .on('mouseout', function() {
                    tooltip.style('display', 'none');
                });
        }

        // Total count label
        chart.append('text')
            .attr('x', chartWidth + 8)
            .attr('y', y + barHeight / 2)
            .attr('dominant-baseline', 'middle')
            .style('font-family', 'Samsung One, sans-serif')
            .style('font-size', '11px')
            .style('fill', '#666')
            .text(d.total.toLocaleString());
    });

    // Legend
    const legend = d3.select(`#${containerId}`)
        .append('div')
        .style('display', 'flex')
        .style('justify-content', 'center')
        .style('gap', '20px')
        .style('margin-top', '12px')
        .style('font-family', 'Samsung One, sans-serif')
        .style('font-size', '11px');

    const sentimentLabels = [
        { key: 'positive', label: 'Positive' },
        { key: 'neutral', label: 'Neutral' },
        { key: 'negative', label: 'Negative' }
    ];

    sentimentLabels.forEach(s => {
        const item = legend.append('div')
            .style('display', 'flex')
            .style('align-items', 'center')
            .style('gap', '6px');

        item.append('div')
            .style('width', '14px')
            .style('height', '14px')
            .style('border-radius', '3px')
            .style('background', SENTIMENT_COLORS[s.key]);

        item.append('span')
            .style('color', '#666')
            .text(s.label);
    });
}

/**
 * Render citation list with URL cards and example prompts
 * @param {string} containerId - DOM element ID
 * @param {Array} data - Array of {url, prompts_count, title, prompts: [{prompt, volume}]}
 */
function renderCitationList(containerId, data) {
    const container = document.getElementById(containerId);

    // Clear existing
    container.innerHTML = '';

    const list = document.createElement('div');
    list.className = 'citation-list';

    data.slice(0, 6).forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'citation-card';

        // Extract display title from URL
        const urlObj = new URL(item.url);
        const pathParts = urlObj.pathname.split('/').filter(p => p);
        const displayTitle = item.title || pathParts[pathParts.length - 1] || urlObj.hostname;

        card.innerHTML = `
            <div class="url-header">
                <span class="url-rank">${index + 1}</span>
                <div class="url-info">
                    <div class="url-title">${displayTitle}</div>
                    <div class="url-path">${urlObj.pathname}</div>
                </div>
                <span class="url-count">${item.prompts_count.toLocaleString()} prompts</span>
            </div>
            <div class="prompts-section">
                <div class="prompts-label">Example prompts triggering this citation</div>
                ${(item.prompts || []).slice(0, 3).map(p => `
                    <div class="prompt-example">
                        <span class="prompt-text">"${p.prompt}"</span>
                        ${p.volume ? `<span class="prompt-volume">${p.volume.toLocaleString()} vol</span>` : ''}
                    </div>
                `).join('')}
            </div>
        `;

        list.appendChild(card);
    });

    container.appendChild(list);
}

/**
 * Render multi-line time series chart for concept trends
 * @param {string} containerId - DOM element ID
 * @param {Array} data - Array of {date, concept, mentions}
 * @param {Array} concepts - List of concept names to display
 */
function renderTrendLines(containerId, data, concepts) {
    const container = document.getElementById(containerId);
    const width = container.clientWidth;
    const height = container.clientHeight - 50; // Reserve space for legend

    // Clear existing
    d3.select(`#${containerId}`).selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    // Filter and prepare data
    const filteredData = data.filter(d => concepts.includes(d.concept));

    // Parse dates
    const parseDate = d3.timeParse('%Y-%m-%d');
    filteredData.forEach(d => {
        d.dateObj = parseDate(d.date);
    });

    // Group by concept
    const grouped = d3.group(filteredData, d => d.concept);

    // Scales
    const xExtent = d3.extent(filteredData, d => d.dateObj);
    const x = d3.scaleTime()
        .domain(xExtent)
        .range([0, chartWidth]);

    const yMax = d3.max(filteredData, d => d.mentions);
    const y = d3.scaleLinear()
        .domain([0, yMax * 1.1])
        .range([chartHeight, 0]);

    // Line colors
    const colors = ['#1428A0', '#01c3b0', '#feb447', '#A50034', '#00A0DF'];
    const colorScale = d3.scaleOrdinal()
        .domain(concepts)
        .range(colors);

    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const chart = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // X axis
    chart.append('g')
        .attr('transform', `translate(0, ${chartHeight})`)
        .call(d3.axisBottom(x).ticks(6).tickFormat(d3.timeFormat('%b %d')))
        .style('font-family', 'Samsung One, sans-serif')
        .style('font-size', '10px');

    // Y axis
    chart.append('g')
        .call(d3.axisLeft(y).ticks(5))
        .style('font-family', 'Samsung One, sans-serif')
        .style('font-size', '10px');

    // Grid lines
    chart.append('g')
        .attr('class', 'grid')
        .call(d3.axisLeft(y).ticks(5).tickSize(-chartWidth).tickFormat(''))
        .style('stroke-opacity', 0.1);

    // Line generator
    const line = d3.line()
        .x(d => x(d.dateObj))
        .y(d => y(d.mentions))
        .curve(d3.curveMonotoneX);

    // Draw lines for each concept
    concepts.forEach((concept, i) => {
        const conceptData = grouped.get(concept);
        if (!conceptData) return;

        // Sort by date
        conceptData.sort((a, b) => a.dateObj - b.dateObj);

        // Draw line
        chart.append('path')
            .datum(conceptData)
            .attr('fill', 'none')
            .attr('stroke', colorScale(concept))
            .attr('stroke-width', 2.5)
            .attr('d', line);

        // Draw dots
        chart.selectAll(`.dot-${i}`)
            .data(conceptData)
            .enter()
            .append('circle')
            .attr('cx', d => x(d.dateObj))
            .attr('cy', d => y(d.mentions))
            .attr('r', 4)
            .attr('fill', colorScale(concept))
            .style('cursor', 'pointer')
            .on('mouseover', function(event, d) {
                d3.select(this).attr('r', 6);
                tooltip.style('display', 'block')
                    .html(`<strong>${d.concept}</strong><br/>
                           ${d3.timeFormat('%b %d, %Y')(d.dateObj)}<br/>
                           ${d.mentions.toLocaleString()} mentions`);
            })
            .on('mousemove', function(event) {
                tooltip.style('left', (event.pageX + 10) + 'px')
                       .style('top', (event.pageY - 10) + 'px');
            })
            .on('mouseout', function() {
                d3.select(this).attr('r', 4);
                tooltip.style('display', 'none');
            });
    });

    // Legend
    const legend = d3.select(`#${containerId}`)
        .append('div')
        .style('display', 'flex')
        .style('justify-content', 'center')
        .style('flex-wrap', 'wrap')
        .style('gap', '16px')
        .style('margin-top', '12px')
        .style('font-family', 'Samsung One, sans-serif')
        .style('font-size', '11px');

    concepts.forEach((concept, i) => {
        const item = legend.append('div')
            .style('display', 'flex')
            .style('align-items', 'center')
            .style('gap', '6px');

        item.append('div')
            .style('width', '20px')
            .style('height', '3px')
            .style('border-radius', '2px')
            .style('background', colorScale(concept));

        item.append('span')
            .style('color', '#666')
            .text(concept);
    });
}

/**
 * Render dual competitor bar charts (branded vs generic)
 * @param {string} containerId - DOM element ID
 * @param {Array} brandedData - Array of {brand_name, mentions}
 * @param {Array} genericData - Array of {brand_name, mentions}
 */
function renderDualCompetitorBars(containerId, brandedData, genericData) {
    const container = document.getElementById(containerId);

    // Clear existing
    container.innerHTML = '';

    const wrapper = document.createElement('div');
    wrapper.className = 'dual-chart-container';

    // Left panel - Branded
    const leftPanel = document.createElement('div');
    leftPanel.className = 'chart-panel';
    leftPanel.innerHTML = `
        <h3>Branded Prompts</h3>
        <div id="${containerId}-branded" style="height: 250px;"></div>
    `;

    // Right panel - Generic
    const rightPanel = document.createElement('div');
    rightPanel.className = 'chart-panel';
    rightPanel.innerHTML = `
        <h3>Generic Prompts</h3>
        <div id="${containerId}-generic" style="height: 250px;"></div>
    `;

    wrapper.appendChild(leftPanel);
    wrapper.appendChild(rightPanel);
    container.appendChild(wrapper);

    // Render each chart after DOM is ready
    setTimeout(() => {
        renderSimpleBars(`${containerId}-branded`, brandedData);
        renderSimpleBars(`${containerId}-generic`, genericData);
    }, 50);
}

/**
 * Render simple horizontal bar chart for competitor comparison
 * @param {string} containerId - DOM element ID
 * @param {Array} data - Array of {brand_name, mentions}
 */
function renderSimpleBars(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    // Sort and take top 5
    const sortedData = data.slice().sort((a, b) => b.mentions - a.mentions).slice(0, 5);
    const maxMentions = d3.max(sortedData, d => d.mentions);

    const margin = { top: 5, right: 60, bottom: 5, left: 70 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    const barHeight = Math.min(36, (chartHeight - 20) / sortedData.length);
    const barGap = 8;

    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const chart = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

    sortedData.forEach((d, i) => {
        const y = i * (barHeight + barGap);
        const barWidth = maxMentions > 0 ? (d.mentions / maxMentions) * chartWidth : 0;
        const brandColor = BRAND_COLORS[d.brand_name] || '#666';
        const isSamsung = d.brand_name === 'Samsung';

        // Brand label
        chart.append('text')
            .attr('x', -8)
            .attr('y', y + barHeight / 2)
            .attr('text-anchor', 'end')
            .attr('dominant-baseline', 'middle')
            .style('font-family', 'Samsung One, sans-serif')
            .style('font-size', '11px')
            .style('font-weight', isSamsung ? '700' : '400')
            .style('fill', brandColor)
            .text(d.brand_name);

        // Background
        chart.append('rect')
            .attr('x', 0)
            .attr('y', y)
            .attr('width', chartWidth)
            .attr('height', barHeight)
            .attr('fill', '#f0f0f0')
            .attr('rx', 4);

        // Value bar
        chart.append('rect')
            .attr('x', 0)
            .attr('y', y)
            .attr('width', barWidth)
            .attr('height', barHeight)
            .attr('fill', brandColor)
            .attr('opacity', isSamsung ? 1 : 0.7)
            .attr('rx', 4);

        // Count label
        chart.append('text')
            .attr('x', chartWidth + 8)
            .attr('y', y + barHeight / 2)
            .attr('dominant-baseline', 'middle')
            .style('font-family', 'Samsung One, sans-serif')
            .style('font-size', '11px')
            .style('font-weight', isSamsung ? '600' : '400')
            .style('fill', '#333')
            .text(d.mentions.toLocaleString());
    });
}

// Create tooltip element
let tooltip;
document.addEventListener('DOMContentLoaded', () => {
    tooltip = d3.select('body')
        .append('div')
        .attr('class', 'chart-tooltip')
        .style('position', 'absolute')
        .style('display', 'none')
        .style('background', 'rgba(0,0,0,0.85)')
        .style('color', '#fff')
        .style('padding', '10px 12px')
        .style('border-radius', '6px')
        .style('font-family', 'Samsung One, sans-serif')
        .style('font-size', '12px')
        .style('line-height', '1.4')
        .style('pointer-events', 'none')
        .style('z-index', '1000')
        .style('box-shadow', '0 4px 12px rgba(0,0,0,0.2)');
});
