/**
 * Shared utility functions for PNP Lock System web interface
 */

/**
 * Parse a JSON file uploaded by the user
 * @param {File} file - The file object from input element
 * @returns {Promise<Object>} - Parsed JSON object
 */
function parseJsonFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = (event) => {
            try {
                const json = JSON.parse(event.target.result);
                resolve(json);
            } catch (error) {
                reject(new Error('Invalid JSON file: ' + error.message));
            }
        };

        reader.onerror = () => {
            reject(new Error('Failed to read file'));
        };

        reader.readAsText(file);
    });
}

/**
 * Download data as a JSON file
 * @param {Object} data - JavaScript object to download
 * @param {string} filename - Name for the downloaded file
 */
function downloadJson(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Validate a lock instance structure
 * @param {Object} instance - Lock instance to validate
 * @returns {Object} - {valid: boolean, error: string}
 */
function validateLockInstance(instance) {
    // Check required fields
    if (!instance.num_dials || typeof instance.num_dials !== 'number') {
        return {valid: false, error: 'Missing or invalid num_dials'};
    }

    if (!Array.isArray(instance.binary_pins)) {
        return {valid: false, error: 'Missing or invalid binary_pins'};
    }

    if (!Array.isArray(instance.negations)) {
        return {valid: false, error: 'Missing or invalid negations'};
    }

    if (!Array.isArray(instance.clauses)) {
        return {valid: false, error: 'Missing or invalid clauses'};
    }

    const numDials = instance.num_dials;

    // Validate binary pins
    for (const dial of instance.binary_pins) {
        if (dial < 1 || dial > numDials) {
            return {valid: false, error: `Binary pin dial ${dial} out of range [1, ${numDials}]`};
        }
    }

    // Check for duplicate binary pins
    if (new Set(instance.binary_pins).size !== instance.binary_pins.length) {
        return {valid: false, error: 'Duplicate binary pins detected'};
    }

    // Validate negations
    for (const neg of instance.negations) {
        if (!Array.isArray(neg) || neg.length !== 2) {
            return {valid: false, error: 'Negation must have exactly 2 dials'};
        }

        const [dial1, dial2] = neg;
        if (dial1 < 1 || dial1 > numDials) {
            return {valid: false, error: `Negation dial ${dial1} out of range [1, ${numDials}]`};
        }
        if (dial2 < 1 || dial2 > numDials) {
            return {valid: false, error: `Negation dial ${dial2} out of range [1, ${numDials}]`};
        }
        if (dial1 === dial2) {
            return {valid: false, error: 'Negation dials must be distinct'};
        }
    }

    // Validate clauses
    for (const clause of instance.clauses) {
        if (!Array.isArray(clause) || clause.length !== 3) {
            return {valid: false, error: 'Clause must have exactly 3 dials'};
        }

        for (const dial of clause) {
            if (dial < 1 || dial > numDials) {
                return {valid: false, error: `Clause dial ${dial} out of range [1, ${numDials}]`};
            }
        }

        if (new Set(clause).size !== 3) {
            return {valid: false, error: 'Clause dials must be distinct'};
        }
    }

    return {valid: true, error: ''};
}

/**
 * Visualize a lock instance on a canvas
 * @param {Object} instance - Lock instance to visualize
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} solution - Optional solution to color dials
 */
function visualizeLock(instance, canvasId, solution = null) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error('Canvas not found:', canvasId);
        return;
    }

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!instance || instance.num_dials === 0) {
        ctx.fillStyle = '#8b949e';
        ctx.font = '18px var(--font-sans)';
        ctx.textAlign = 'center';
        ctx.fillText('No instance loaded', canvas.width / 2, canvas.height / 2);
        return;
    }

    // Calculate dial positions in a circle
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.35;

    const dialPositions = [];
    for (let i = 0; i < instance.num_dials; i++) {
        const angle = (i / instance.num_dials) * 2 * Math.PI - Math.PI / 2;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        dialPositions.push({x, y, number: i + 1});
    }

    // Draw negations (red lines)
    ctx.strokeStyle = '#f85149';
    ctx.lineWidth = 3;
    instance.negations.forEach(neg => {
        const pos1 = dialPositions[neg[0] - 1];
        const pos2 = dialPositions[neg[1] - 1];
        ctx.beginPath();
        ctx.moveTo(pos1.x, pos1.y);
        ctx.lineTo(pos2.x, pos2.y);
        ctx.stroke();
    });

    // Draw clauses (green triangles)
    ctx.strokeStyle = '#3fb950';
    ctx.lineWidth = 2;
    ctx.fillStyle = 'rgba(63, 185, 80, 0.1)';
    instance.clauses.forEach(clause => {
        const pos1 = dialPositions[clause[0] - 1];
        const pos2 = dialPositions[clause[1] - 1];
        const pos3 = dialPositions[clause[2] - 1];

        ctx.beginPath();
        ctx.moveTo(pos1.x, pos1.y);
        ctx.lineTo(pos2.x, pos2.y);
        ctx.lineTo(pos3.x, pos3.y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    });

    // Draw dials (colored by solution if provided)
    dialPositions.forEach(pos => {
        let dialColor = '#58a6ff'; // Default blue

        if (solution && solution.dial_values) {
            const value = solution.dial_values[pos.number.toString()] || solution.dial_values[pos.number];
            if (value === 1) {
                dialColor = '#f85149'; // Red for FALSE
            } else if (value === 6) {
                dialColor = '#3fb950'; // Green for TRUE
            }
        }

        // Circle
        ctx.fillStyle = dialColor;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 25, 0, 2 * Math.PI);
        ctx.fill();

        // Number
        ctx.fillStyle = '#0d1117';
        ctx.font = 'bold 16px var(--font-sans)';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(pos.number, pos.x, pos.y);
    });
}

/**
 * Verify a solution against a lock instance
 * @param {Object} instance - Lock instance
 * @param {Object} solution - Solution with dial_values
 * @returns {Object} - {valid: boolean, errors: Array<string>}
 */
function verifySolution(instance, solution) {
    const errors = [];

    // Check all dials are set
    for (let dial = 1; dial <= instance.num_dials; dial++) {
        const value = solution.dial_values[dial.toString()] || solution.dial_values[dial];
        if (value === undefined) {
            errors.push(`Dial ${dial} is not set`);
            continue;
        }

        // Check binary pin constraint
        if (instance.binary_pins.includes(dial) && value !== 1 && value !== 6) {
            errors.push(`Dial ${dial}: invalid value ${value} (must be 1 or 6)`);
        }
    }

    // Check negations
    instance.negations.forEach(([dial1, dial2], index) => {
        const val1 = solution.dial_values[dial1.toString()] || solution.dial_values[dial1];
        const val2 = solution.dial_values[dial2.toString()] || solution.dial_values[dial2];
        const sum = val1 + val2;

        if (sum !== 7) {
            errors.push(`Negation Not(${dial1}, ${dial2}): ${val1} + ${val2} = ${sum} (expected 7)`);
        }
    });

    // Check clauses
    instance.clauses.forEach(([dial1, dial2, dial3], index) => {
        const val1 = solution.dial_values[dial1.toString()] || solution.dial_values[dial1];
        const val2 = solution.dial_values[dial2.toString()] || solution.dial_values[dial2];
        const val3 = solution.dial_values[dial3.toString()] || solution.dial_values[dial3];
        const sum = val1 + val2 + val3;

        if (sum < 8) {
            errors.push(`Clause OR(${dial1}, ${dial2}, ${dial3}): ${val1} + ${val2} + ${val3} = ${sum} (expected ≥ 8)`);
        }
    });

    return {
        valid: errors.length === 0,
        errors: errors
    };
}

/**
 * Format a lock instance for display
 * @param {Object} instance - Lock instance
 * @returns {string} - Formatted HTML string
 */
function formatInstanceDisplay(instance) {
    let html = '<div class="instance-details">';
    html += `<div><strong>Dials:</strong> ${instance.num_dials}</div>`;
    html += `<div><strong>Binary Pins:</strong> ${instance.binary_pins.length} (all dials)</div>`;
    html += `<div><strong>Negations:</strong> ${instance.negations.length}</div>`;
    html += `<div><strong>Clauses:</strong> ${instance.clauses.length}</div>`;

    if (instance.negations.length > 0) {
        html += '<div style="margin-top: 10px;"><strong>Negation Links:</strong><ul>';
        instance.negations.forEach(neg => {
            html += `<li>Not(${neg[0]}, ${neg[1]})</li>`;
        });
        html += '</ul></div>';
    }

    if (instance.clauses.length > 0) {
        html += '<div style="margin-top: 10px;"><strong>OR Clauses:</strong><ul>';
        instance.clauses.forEach(clause => {
            html += `<li>OR(${clause[0]}, ${clause[1]}, ${clause[2]})</li>`;
        });
        html += '</ul></div>';
    }

    html += '</div>';
    return html;
}

/**
 * Show a temporary message to the user
 * @param {HTMLElement} element - Element to show message in
 * @param {string} message - Message text
 * @param {string} type - 'success' or 'error'
 * @param {number} duration - Duration in ms (default 3000)
 */
function showMessage(element, message, type = 'success', duration = 3000) {
    const className = type === 'error' ? 'error-message' : 'success-message';
    element.innerHTML = `<div class="${className}">${message}</div>`;

    if (duration > 0) {
        setTimeout(() => {
            element.innerHTML = '';
        }, duration);
    }
}
