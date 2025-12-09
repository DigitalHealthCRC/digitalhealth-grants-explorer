// Grants Application JavaScript
class GrantsApp {
    constructor() {
        this.grants = [];
        this.filteredGrants = [];
        this.filters = {
            keyword: '',
            minAmount: null,
            maxAmount: null,
            complexity: '',
            body: '',
            sortBy: '',
            selectedTags: new Set()
        };

        this.init();
    }

    async init() {
        await this.loadGrants();
        this.setupEventListeners();
        this.populateFilterDropdowns();
        this.renderGrants();
        this.updateResultsCount();
    }

    async loadGrants() {
        try {
            const response = await fetch('data.csv');
            const csvText = await response.text();
            this.grants = this.parseCSVToGrants(csvText);
            this.filteredGrants = [...this.grants];
        } catch (error) {
            console.error('Error loading grants from CSV, trying fallback data:', error);
            this.loadFallbackData();
        }
    }

    loadFallbackData() {
        console.error('No fallback data available');
        this.showErrorState();
    }

    parseCSVToGrants(csvText) {
        const lines = csvText.split('\n').filter(line => line.trim());
        if (lines.length < 2) return [];

        const headers = lines[0].split(',').map(h => h.trim());
        const grants = [];

        for (let i = 1; i < lines.length; i++) {
            const values = this.parseCSVLine(lines[i]);
            if (values.length === headers.length) {
                const grant = this.createGrantFromCSV(headers, values);
                if (grant) grants.push(grant);
            }
        }

        return grants;
    }

    parseCSVLine(line) {
        const values = [];
        let current = '';
        let inQuotes = false;

        for (let i = 0; i < line.length; i++) {
            const char = line[i];

            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                values.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }

        values.push(current.trim());
        return values;
    }

    createGrantFromCSV(headers, values) {
        try {
            const grant = {};

            for (let i = 0; i < headers.length; i++) {
                const header = headers[i];
                const value = values[i];

                switch (header) {
                    case 'Grant Name':
                        grant.grant_name = value;
                        break;
                    case 'Administering Body':
                        grant.administering_body = value;
                        break;
                    case 'Grant Purpose':
                        grant.purpose = value;
                        break;
                    case 'Application Deadline':
                        grant.deadlines = value ? [value] : [];
                        break;
                    case 'Funding Amount':
                        grant.funding = { amount: value };
                        break;
                    case 'Co-contribution Requirements':
                        grant.co_contribution = value === 'None specified' ? null : value;
                        break;
                    case 'Eligibility Criteria':
                        grant.eligibility = value;
                        break;
                    case 'Assessment Criteria':
                        grant.assessment = value;
                        break;
                    case 'Level of Complexity':
                        grant.complexity = value;
                        break;
                    case 'Web Link':
                        grant.references = value ? [value] : [];
                        break;
                    case 'Expired':
                        grant.expired = value;
                        break;
                }
            }

            // Filter out expired grants
            if (grant.expired && grant.expired.toLowerCase() === 'yes') {
                return null;
            }

            // Generate tags from key fields
            grant.tags = this.generateTagsFromGrant(grant);

            return grant;
        } catch (error) {
            console.error('Error creating grant from CSV:', error);
            return null;
        }
    }

    generateTagsFromGrant(grant) {
        const tags = [];

        // Create searchable text from grant name and purpose
        const searchableText = `${grant.grant_name || ''} ${grant.purpose || ''}`.toLowerCase();

        // Add tags based on grant name and purpose
        if (searchableText.includes('research')) tags.push('#Research');
        if (searchableText.includes('health')) tags.push('#Health');
        if (searchableText.includes('medical')) tags.push('#Medical');
        if (searchableText.includes('innovation') || searchableText.includes('innovative')) tags.push('#Innovation');
        if (searchableText.includes('mrff')) tags.push('#MRFF');
        if (searchableText.includes('clinical')) tags.push('#Clinical');
        if (searchableText.includes('trial')) tags.push('#ClinicalTrials');
        if (searchableText.includes('stem cell')) tags.push('#StemCell');
        if (searchableText.includes('cardiovascular')) tags.push('#Cardiovascular');
        if (searchableText.includes('cancer')) tags.push('#Cancer');
        if (searchableText.includes('dementia') || searchableText.includes('ageing')) tags.push('#Dementia');
        if (searchableText.includes('diabetes')) tags.push('#Diabetes');

        // Add innovation and digital transformation tags
        if (searchableText.includes('digital') && (searchableText.includes('transformation') || searchableText.includes('transform'))) {
            tags.push('#DigitalTransformation');
        }
        if (searchableText.includes('workforce') && searchableText.includes('health')) {
            tags.push('#HealthWorkforce');
        }
        if (searchableText.includes('digital') && searchableText.includes('workforce') && searchableText.includes('health')) {
            tags.push('#DigitalHealthWorkforce');
        }
        if (searchableText.includes('digital') && searchableText.includes('health')) {
            tags.push('#DigitalHealth');
        }

        // Add geographic tags
        if (grant.administering_body) {
            const geographicTags = this.getGeographicTags(grant.administering_body);
            tags.push(...geographicTags);

            // Add specific organization tags
            const adminBody = grant.administering_body.toLowerCase();
            if (adminBody.includes('nhmrc')) tags.push('#NHMRC');
            if (adminBody.includes('arc')) tags.push('#ARC');
        }

        // Add complexity tag
        if (grant.complexity) {
            tags.push(`#${grant.complexity.replace(/\s+/g, '').replace(/[^\w]/g, '')}`);
        }

        return [...new Set(tags)]; // Remove duplicates
    }

    getGeographicTags(administeringBody) {
        const tags = [];
        const adminBody = administeringBody.toLowerCase();

        // Check for New Zealand
        const nzIndicators = ['new zealand', 'nz', 'mbie', 'tec', 'hrc', 'callaghan innovation',
            'ministry of business, innovation and employment', 'tertiary education commission',
            'health research council of new zealand'];
        if (nzIndicators.some(indicator => adminBody.includes(indicator))) {
            tags.push('#NewZealand');
            return tags;
        }

        // Check for international organizations
        const intlIndicators = ['gates foundation', 'bill & melinda gates', 'unesco', 'chan zuckerberg',
            'wellcome trust', 'open philanthropy', 'global innovation fund',
            'grand challenges canada', 'american australian association'];
        if (intlIndicators.some(indicator => adminBody.includes(indicator))) {
            tags.push('#International');
            return tags;
        }

        // Check for Australian organizations
        const australianIndicators = ['australian', 'australia', 'commonwealth', 'federal', 'nhmrc', 'arc',
            'csiro', 'austcyber', 'arena', 'ato', 'department of', 'mrff'];

        if (australianIndicators.some(indicator => adminBody.includes(indicator))) {
            tags.push('#Australia');

            // Check for Commonwealth/Federal
            const commonwealthIndicators = ['commonwealth', 'federal', 'australian government', 'department of',
                'nhmrc', 'arc', 'csiro', 'ato', 'mrff', 'austcyber', 'arena'];
            if (commonwealthIndicators.some(indicator => adminBody.includes(indicator))) {
                tags.push('#Commonwealth');
            }

            // Check for specific Australian states
            if (['nsw', 'new south wales', 'sydney', 'investment nsw'].some(indicator => adminBody.includes(indicator))) {
                tags.push('#NSW');
            } else if (['victoria', 'victorian', 'melbourne', 'vic'].some(indicator => adminBody.includes(indicator))) {
                tags.push('#Victoria');
            } else if (['queensland', 'qld', 'brisbane'].some(indicator => adminBody.includes(indicator))) {
                tags.push('#Queensland');
            } else if (['western australia', 'wa', 'perth'].some(indicator => adminBody.includes(indicator))) {
                tags.push('#WesternAustralia');
            } else if (['south australia', 'sa', 'adelaide'].some(indicator => adminBody.includes(indicator))) {
                tags.push('#SouthAustralia');
            } else if (['tasmania', 'tas', 'hobart', 'tasmanian'].some(indicator => adminBody.includes(indicator))) {
                tags.push('#Tasmania');
            } else if (['northern territory', 'nt', 'darwin'].some(indicator => adminBody.includes(indicator))) {
                tags.push('#NorthernTerritory');
            } else if (['act', 'australian capital territory', 'canberra'].some(indicator => adminBody.includes(indicator))) {
                tags.push('#ACT');
            }
        }

        return tags;
    }

    parseDeadlineDate(deadlineText) {
        if (!deadlineText) return null;

        // Handle various date formats
        const datePatterns = [
            /(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})/i,
            /(\d{1,2})\/(\d{1,2})\/(\d{4})/,
            /(\d{4})-(\d{1,2})-(\d{1,2})/
        ];

        const monthNames = {
            'january': 0, 'february': 1, 'march': 2, 'april': 3, 'may': 4, 'june': 5,
            'july': 6, 'august': 7, 'september': 8, 'october': 9, 'november': 10, 'december': 11
        };

        for (const pattern of datePatterns) {
            const match = deadlineText.match(pattern);
            if (match) {
                if (pattern.source.includes('January|February')) {
                    // Format: "31 March 2025"
                    const day = parseInt(match[1]);
                    const month = monthNames[match[2].toLowerCase()];
                    const year = parseInt(match[3]);
                    return new Date(year, month, day);
                } else if (pattern.source.includes('\\/')) {
                    // Format: "31/03/2025" (DD/MM/YYYY)
                    const day = parseInt(match[1]);
                    const month = parseInt(match[2]) - 1;
                    const year = parseInt(match[3]);
                    return new Date(year, month, day);
                } else {
                    // Format: "2025-03-31" (YYYY-MM-DD)
                    const year = parseInt(match[1]);
                    const month = parseInt(match[2]) - 1;
                    const day = parseInt(match[3]);
                    return new Date(year, month, day);
                }
            }
        }

        return null;
    }

    getEarliestDeadline(grant) {
        if (!grant.deadlines || grant.deadlines.length === 0) return null;

        const dates = grant.deadlines
            .map(deadline => this.parseDeadlineDate(deadline))
            .filter(date => date !== null)
            .sort((a, b) => a - b);

        return dates.length > 0 ? dates[0] : null;
    }

    getComplexityOrder(complexity) {
        if (!complexity) return 5;

        const complexityLower = complexity.toLowerCase();
        if (complexityLower.includes('simple')) return 1;
        if (complexityLower.includes('moderate')) return 2;
        if (complexityLower.includes('complex') && !complexityLower.includes('very')) return 3;
        if (complexityLower.includes('very') || complexityLower.includes('high')) return 4;
        return 5;
    }

    sortGrants(grants, sortBy) {
        if (!sortBy) return grants;

        const sortedGrants = [...grants];

        switch (sortBy) {
            case 'deadline':
                return sortedGrants.sort((a, b) => {
                    const dateA = this.getEarliestDeadline(a);
                    const dateB = this.getEarliestDeadline(b);

                    // Handle cases where dates are null
                    if (!dateA && !dateB) return 0;
                    if (!dateA) return 1; // Put grants without deadlines at the end
                    if (!dateB) return -1;

                    return dateA - dateB;
                });

            case 'amount':
                return sortedGrants.sort((a, b) => {
                    const amountA = this.extractFundingAmount(a);
                    const amountB = this.extractFundingAmount(b);
                    return amountB - amountA; // High to low
                });

            case 'complexity':
                return sortedGrants.sort((a, b) => {
                    const orderA = this.getComplexityOrder(a.complexity);
                    const orderB = this.getComplexityOrder(b.complexity);
                    return orderA - orderB; // Simple to complex
                });

            default:
                return sortedGrants;
        }
    }

    setupEventListeners() {
        // Keyword filter
        const keywordFilter = document.getElementById('keywordFilter');
        keywordFilter.addEventListener('input', (e) => {
            this.filters.keyword = e.target.value.toLowerCase();
            this.applyFilters();
        });

        // Amount filters
        const minAmountFilter = document.getElementById('minAmountFilter');
        const maxAmountFilter = document.getElementById('maxAmountFilter');

        minAmountFilter.addEventListener('input', (e) => {
            this.filters.minAmount = e.target.value ? parseFloat(e.target.value) : null;
            this.applyFilters();
        });

        maxAmountFilter.addEventListener('input', (e) => {
            this.filters.maxAmount = e.target.value ? parseFloat(e.target.value) : null;
            this.applyFilters();
        });

        // Complexity filter
        const complexityFilter = document.getElementById('complexityFilter');
        complexityFilter.addEventListener('change', (e) => {
            this.filters.complexity = e.target.value;
            this.applyFilters();
        });

        // Body filter
        const bodyFilter = document.getElementById('bodyFilter');
        bodyFilter.addEventListener('change', (e) => {
            this.filters.body = e.target.value;
            this.applyFilters();
        });

        // Sort filter
        const sortFilter = document.getElementById('sortFilter');
        sortFilter.addEventListener('change', (e) => {
            this.filters.sortBy = e.target.value;
            this.applyFilters();
        });

        // Clear filters
        const clearFilters = document.getElementById('clearFilters');
        clearFilters.addEventListener('click', () => {
            this.clearAllFilters();
        });

        // Export CSV
        const exportCSV = document.getElementById('exportCSV');
        exportCSV.addEventListener('click', () => {
            this.exportToCSV();
        });

        // Modal event listeners
        const modal = document.getElementById('grantModal');
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeGrantModal();
            }
        });

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeGrantModal();
            }
        });
    }

    populateFilterDropdowns() {
        // Populate administering bodies
        const bodies = [...new Set(this.grants.map(grant => grant.administering_body))].sort();
        const bodyFilter = document.getElementById('bodyFilter');

        bodies.forEach(body => {
            const option = document.createElement('option');
            option.value = body;
            option.textContent = body;
            bodyFilter.appendChild(option);
        });

        // Populate tag filters
        this.populateTagFilters();
    }

    populateTagFilters() {
        // Collect all unique tags from grants
        const allTags = new Set();
        this.grants.forEach(grant => {
            if (grant.tags && Array.isArray(grant.tags)) {
                grant.tags.forEach(tag => {
                    // Remove # prefix if present for display
                    const cleanTag = tag.startsWith('#') ? tag.slice(1) : tag;
                    allTags.add(cleanTag);
                });
            }
        });

        // Sort tags alphabetically
        const sortedTags = Array.from(allTags).sort();

        // Create tag filter elements
        const tagFiltersContainer = document.getElementById('tagFilters');
        tagFiltersContainer.innerHTML = '';

        sortedTags.forEach(tag => {
            const tagElement = document.createElement('span');
            tagElement.className = 'filter-tag';
            tagElement.textContent = tag;
            tagElement.dataset.tag = tag;
            tagElement.tabIndex = 0;
            tagElement.setAttribute('role', 'button');
            tagElement.setAttribute('aria-pressed', 'false');
            tagElement.addEventListener('click', () => this.toggleTagFilter(tag));
            tagElement.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleTagFilter(tag);
                }
            });
            tagFiltersContainer.appendChild(tagElement);
        });
    }

    toggleTagFilter(tag) {
        if (this.filters.selectedTags.has(tag)) {
            this.filters.selectedTags.delete(tag);
        } else {
            this.filters.selectedTags.add(tag);
        }

        // Update visual state of tag elements
        this.updateTagFilterVisuals();

        // Apply filters
        this.applyFilters();
    }

    updateTagFilterVisuals() {
        const tagElements = document.querySelectorAll('.filter-tag');
        tagElements.forEach(element => {
            const tag = element.dataset.tag;
            if (this.filters.selectedTags.has(tag)) {
                element.classList.add('active');
                element.setAttribute('aria-pressed', 'true');
            } else {
                element.classList.remove('active');
                element.setAttribute('aria-pressed', 'false');
            }
        });
    }

    extractFundingAmount(grant) {
        if (!grant.funding || !grant.funding.amount) return 0;

        const amountStr = grant.funding.amount.toLowerCase();

        // Extract numbers and convert to millions for easier comparison
        if (amountStr.includes('million')) {
            const match = amountStr.match(/[\d,]+\.?\d*/);
            return match ? parseFloat(match[0].replace(',', '')) * 1000000 : 0;
        } else if (amountStr.includes('$')) {
            const match = amountStr.match(/[\d,]+/g);
            if (match && match.length > 0) {
                return parseFloat(match[match.length - 1].replace(',', ''));
            }
        }

        return 0;
    }

    applyFilters() {
        this.filteredGrants = this.grants.filter(grant => {
            // Keyword filter
            if (this.filters.keyword) {
                const keyword = this.filters.keyword;
                const searchableText = [
                    grant.grant_name,
                    grant.purpose,
                    grant.administering_body,
                    grant.comments,
                    ...(grant.tags || [])
                ].join(' ').toLowerCase();

                if (!searchableText.includes(keyword)) return false;
            }

            // Amount filters
            const grantAmount = this.extractFundingAmount(grant);
            if (this.filters.minAmount && grantAmount < this.filters.minAmount) return false;
            if (this.filters.maxAmount && grantAmount > this.filters.maxAmount) return false;

            // Complexity filter
            if (this.filters.complexity && grant.complexity !== this.filters.complexity) return false;

            // Body filter
            if (this.filters.body && grant.administering_body !== this.filters.body) return false;

            // Tag filter
            if (this.filters.selectedTags.size > 0) {
                const grantTags = grant.tags ? grant.tags.map(tag =>
                    tag.startsWith('#') ? tag.slice(1) : tag
                ) : [];

                // Check if grant has at least one of the selected tags
                const hasSelectedTag = Array.from(this.filters.selectedTags).some(selectedTag =>
                    grantTags.includes(selectedTag)
                );

                if (!hasSelectedTag) return false;
            }

            return true;
        });

        // Apply sorting
        this.filteredGrants = this.sortGrants(this.filteredGrants, this.filters.sortBy);

        this.renderGrants();
        this.updateResultsCount();

        // Announce filter change to screen readers
        const resultCount = this.filteredGrants.length;
        this.announceToScreenReader(`Filters applied. ${resultCount} grants found.`);
    }

    clearAllFilters() {
        // Clear filter inputs
        document.getElementById('keywordFilter').value = '';
        document.getElementById('minAmountFilter').value = '';
        document.getElementById('maxAmountFilter').value = '';
        document.getElementById('complexityFilter').value = '';
        document.getElementById('bodyFilter').value = '';
        document.getElementById('sortFilter').value = '';

        // Reset filters
        this.filters = {
            keyword: '',
            minAmount: null,
            maxAmount: null,
            complexity: '',
            body: '',
            sortBy: '',
            selectedTags: new Set()
        };

        // Update tag filter visuals
        this.updateTagFilterVisuals();

        this.filteredGrants = [...this.grants];
        this.renderGrants();
        this.updateResultsCount();

        // Announce filter clear to screen readers
        this.announceToScreenReader(`All filters cleared. ${this.filteredGrants.length} grants shown.`);
    }

    formatFunding(funding) {
        if (!funding) return 'Not specified';

        let result = [];
        if (funding.amount) result.push(`Amount: ${funding.amount}`);
        if (funding.total_pool) result.push(`Total Pool: ${funding.total_pool}`);
        if (funding.coverage) result.push(`Coverage: ${funding.coverage}`);

        return result.join(' | ') || 'Not specified';
    }

    formatDeadlines(deadlines) {
        if (!deadlines || deadlines.length === 0) return [];
        return Array.isArray(deadlines) ? deadlines : [deadlines];
    }

    formatTags(tags) {
        if (!tags || !Array.isArray(tags)) return [];
        return tags.map(tag => tag.startsWith('#') ? tag.slice(1) : tag);
    }

    getComplexityClass(complexity) {
        if (!complexity) return '';
        return complexity.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '');
    }

    createGrantCard(grant, index) {
        return `
            <div class="grant-card" 
                 data-grant-index="${index}" 
                 tabindex="0"
                 role="button"
                 aria-label="Grant: ${grant.grant_name} - ${grant.administering_body}. Press Enter for details"
                 onclick="grantsApp.showGrantModal(${index})"
                 onkeydown="grantsApp.handleCardKeydown(event, ${index})">
                <div class="grant-title">${grant.grant_name}</div>
                <div class="grant-body">${grant.administering_body}</div>
                <div class="grant-funding">${this.formatFunding(grant.funding)}</div>
                <div class="click-hint">Click or press Enter for details</div>
            </div>
        `;
    }

    handleCardKeydown(event, index) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            this.showGrantModal(index);
        }
    }

    showGrantModal(index) {
        const grant = this.filteredGrants[index];
        if (!grant) return;

        const deadlines = this.formatDeadlines(grant.deadlines);
        const tags = this.formatTags(grant.tags);
        const complexityClass = this.getComplexityClass(grant.complexity);

        // Create modal content
        const modalContent = `
            <div class="modal-header">
                <h2 id="modal-title">${grant.grant_name}</h2>
                <button class="modal-close" onclick="grantsApp.closeGrantModal()" aria-label="Close modal">&times;</button>
            </div>
            <div class="modal-body" id="modal-description">
                <div class="modal-section">
                    <strong>Administering Body:</strong> ${grant.administering_body}
                </div>
                
                <div class="modal-section">
                    <strong>Funding:</strong> ${this.formatFunding(grant.funding)}
                </div>
                
                <div class="modal-section">
                    <strong>Purpose:</strong> ${grant.purpose}
                </div>
                
                <div class="modal-section">
                    <strong>Complexity:</strong> 
                    <span class="complexity ${complexityClass}">${grant.complexity || 'Not specified'}</span>
                </div>
                
                <div class="modal-section">
                    <strong>Eligibility:</strong> ${grant.eligibility || 'See guidelines'}
                </div>
                
                ${grant.assessment ? `
                    <div class="modal-section">
                        <strong>Assessment Criteria:</strong> ${grant.assessment}
                    </div>
                ` : ''}
                
                ${deadlines.length > 0 ? `
                    <div class="modal-section">
                        <strong>Application Deadlines:</strong>
                        <ul class="modal-list">
                            ${deadlines.map(deadline => `<li>${deadline}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${grant.opens ? `
                    <div class="modal-section">
                        <strong>Opens:</strong> ${grant.opens}
                    </div>
                ` : ''}
                
                ${grant.co_contribution ? `
                    <div class="modal-section">
                        <strong>Co-contribution:</strong> ${grant.co_contribution}
                    </div>
                ` : ''}
                
                ${grant.references && grant.references.length > 0 ? `
                    <div class="modal-section">
                        <strong>More Information:</strong>
                        <div class="modal-links">
                            ${grant.references.map(ref => `<a href="${ref}" target="_blank" rel="noopener">Application Link</a>`).join(' | ')}
                        </div>
                    </div>
                ` : ''}
                
                ${tags.length > 0 ? `
                    <div class="modal-section">
                        <strong>Tags:</strong>
                        <div class="modal-tags">
                            ${tags.map(tag => `<span class="modal-tag">${tag}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        // Show modal
        const modal = document.getElementById('grantModal');
        const modalContentElement = modal.querySelector('.modal-content');
        modalContentElement.innerHTML = modalContent;
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling

        // Store the currently focused element for restoration later
        this.previouslyFocusedElement = document.activeElement;

        // Focus the close button when modal opens
        setTimeout(() => {
            const closeButton = modal.querySelector('.modal-close');
            if (closeButton) {
                closeButton.focus();
            }
        }, 100);

        // Setup focus trapping
        this.setupFocusTrap(modal);

        // Announce modal opening to screen readers
        this.announceToScreenReader(`Grant details modal opened for ${grant.grant_name}`);
    }

    closeGrantModal() {
        const modal = document.getElementById('grantModal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restore scrolling

        // Remove focus trap
        this.removeFocusTrap();

        // Restore focus to the previously focused element
        if (this.previouslyFocusedElement) {
            this.previouslyFocusedElement.focus();
            this.previouslyFocusedElement = null;
        }

        // Announce modal closing to screen readers
        this.announceToScreenReader('Grant details modal closed');
    }

    setupFocusTrap(modal) {
        // Get all focusable elements within the modal
        this.focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        this.firstFocusableElement = this.focusableElements[0];
        this.lastFocusableElement = this.focusableElements[this.focusableElements.length - 1];

        // Add event listener for tab trapping
        this.trapFocusHandler = (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    // Shift + Tab
                    if (document.activeElement === this.firstFocusableElement) {
                        this.lastFocusableElement.focus();
                        e.preventDefault();
                    }
                } else {
                    // Tab
                    if (document.activeElement === this.lastFocusableElement) {
                        this.firstFocusableElement.focus();
                        e.preventDefault();
                    }
                }
            }
        };

        modal.addEventListener('keydown', this.trapFocusHandler);
    }

    removeFocusTrap() {
        const modal = document.getElementById('grantModal');
        if (this.trapFocusHandler) {
            modal.removeEventListener('keydown', this.trapFocusHandler);
            this.trapFocusHandler = null;
        }
    }

    announceToScreenReader(message) {
        const announcer = document.getElementById('screen-reader-announcements');
        if (announcer) {
            announcer.textContent = message;
            // Clear the message after announcement
            setTimeout(() => {
                announcer.textContent = '';
            }, 1000);
        }
    }

    renderGrants() {
        const grantsGrid = document.getElementById('grantsGrid');

        if (this.filteredGrants.length === 0) {
            grantsGrid.innerHTML = `
                <div class="no-grants">
                    <div class="no-grants-icon" aria-hidden="true">No results</div>
                    <p>No grants match your current filters.</p>
                    <p>Try adjusting your search criteria.</p>
                </div>
            `;
            return;
        }

        grantsGrid.innerHTML = this.filteredGrants
            .map((grant, index) => this.createGrantCard(grant, index))
            .join('');
    }

    updateResultsCount() {
        const resultsCount = document.getElementById('resultsCount');
        resultsCount.textContent = this.filteredGrants.length;
    }

    exportToCSV() {
        if (this.filteredGrants.length === 0) {
            alert('No grants to export. Please adjust your filters.');
            this.announceToScreenReader('Export failed. No grants to export.');
            return;
        }

        // Define CSV headers matching the original data.csv structure
        const headers = [
            'Grant Name',
            'Administering Body',
            'Grant Purpose',
            'Application Deadline',
            'Funding Amount',
            'Co-contribution Requirements',
            'Eligibility Criteria',
            'Assessment Criteria',
            'Application Complexity',
            'Web Link',
            'Level of Complexity'
        ];

        // Convert grants to CSV format
        const csvRows = [headers.join(',')];

        this.filteredGrants.forEach(grant => {
            const row = [
                this.escapeCSVField(grant.grant_name || ''),
                this.escapeCSVField(grant.administering_body || ''),
                this.escapeCSVField(grant.purpose || ''),
                this.escapeCSVField(grant.deadlines ? grant.deadlines.join('; ') : ''),
                this.escapeCSVField(grant.funding ? grant.funding.amount || '' : ''),
                this.escapeCSVField(grant.co_contribution || 'None specified'),
                this.escapeCSVField(grant.eligibility || ''),
                this.escapeCSVField(grant.assessment || ''),
                this.escapeCSVField(''), // Application Complexity (legacy field, empty)
                this.escapeCSVField(grant.references ? grant.references.join('; ') : ''),
                this.escapeCSVField(grant.complexity || '') // Level of Complexity
            ];
            csvRows.push(row.join(','));
        });

        // Create and download the CSV file
        const csvContent = csvRows.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

        // Generate filename with current date and filter info
        const now = new Date();
        const dateStr = now.toISOString().split('T')[0]; // YYYY-MM-DD
        const filterSuffix = this.filters.sortBy ? `_sorted_by_${this.filters.sortBy}` : '';
        const filename = `healthcare_grants_${dateStr}${filterSuffix}.csv`;

        // Create download link
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);

            // Show success message
            this.showExportSuccess(this.filteredGrants.length, filename);

            // Announce export success to screen readers
            this.announceToScreenReader(`CSV export successful. ${this.filteredGrants.length} grants exported to ${filename}`);
        } else {
            alert('Your browser does not support automatic downloads. Please try a different browser.');
        }
    }

    escapeCSVField(field) {
        if (!field) return '""';

        // Convert field to string and handle quotes
        const stringField = String(field);

        // If field contains comma, quote, or newline, wrap in quotes and escape internal quotes
        if (stringField.includes(',') || stringField.includes('"') || stringField.includes('\n')) {
            return '"' + stringField.replace(/"/g, '""') + '"';
        }

        return stringField;
    }

    showExportSuccess(count, filename) {
        // Create temporary success message
        const message = document.createElement('div');
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 255, 136, 0.2);
            border: 1px solid rgba(0, 255, 136, 0.4);
            color: #00ff88;
            padding: 15px 20px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
            font-size: 0.9em;
        `;
        message.textContent = `Exported ${count} grants to ${filename}`;

        document.body.appendChild(message);

        // Remove message after 3 seconds
        setTimeout(() => {
            if (document.body.contains(message)) {
                document.body.removeChild(message);
            }
        }, 3000);
    }

    showErrorState() {
        const grantsGrid = document.getElementById('grantsGrid');
        grantsGrid.innerHTML = `
            <div class="no-grants">
                <div class="no-grants-icon" aria-hidden="true">Error</div>
                <p>Error loading grants data.</p>
                <p>Please check that the data.csv file is available.</p>
            </div>
        `;
    }
}

// Initialize the app when DOM is loaded
let grantsApp;
document.addEventListener('DOMContentLoaded', () => {
    grantsApp = new GrantsApp();
});
