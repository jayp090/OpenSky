const initChart = (data) => {
    // Basic check to see if we actually have data and to prvent a null error
    if (!data || data.length === 0) {
        console.warn("No data received from API. Chart will be empty.");
        document.getElementById('cy').innerHTML = 
            '<p style="padding:20px; color:gray;">No team data available to display.</p>';
        return;
    }

    var cy = cytoscape({
        container: document.getElementById('cy'),
        elements: data,
        
        style: [
            {
                // Styling for Individual Teams
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'background-color': '#00558E', // Sky Blue
                    'color': '#000',
                    'font-size': '10px',
                    'text-valign': 'bottom',
                    'text-margin-y': '5px',
                    'width': '25px',
                    'height': '25px',
                    'z-index': 10
                }
            },
            {
                // Styling for Department Clusters (the "containers")
                selector: ':parent',
                style: {
                    'background-opacity': 0.1,
                    'background-color': '#00558E',
                    'border-color': '#00558E',
                    'border-width': 2,
                    'label': 'data(label)',
                    'text-valign': 'top',
                    'font-weight': 'bold',
                    'font-size': '14px'
                }
            },
            {
                // Styling for Dependency Arrows
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#999',
                    'target-arrow-shape': 'triangle',
                    'target-arrow-color': '#999',
                    'curve-style': 'bezier', // Required for arrowheads to show on curved lines
                    'opacity': 0.6
                }
            },
            {
                // Highlighted state (for future interactivity)
                selector: '.highlighted',
                style: {
                    'line-color': '#FF5733',
                    'target-arrow-color': '#FF5733',
                    'width': 4,
                    'opacity': 1.0
                }
            }
        ],

        layout: {
            name: 'grid', // This is the simplest layout possible
            
            rows: 7       // Since you have 46 teams, 7x7 will fit them all
        }
    });

    // Optional: Interactive highlight on hover
    cy.on('mouseover', 'node', function(e) {
        var node = e.target;
        // Highlight all downstream teams (successors)
        node.successors().addClass('highlighted');
    });

    cy.on('mouseout', 'node', function(e) {
        var node = e.target;
        node.successors().removeClass('highlighted');
    });

    // Click a team node to go to its detail page
    cy.on('tap', 'node', function(e) {
        var node = e.target;
        var nodeId = node.data('id');
        // Department nodes have id like 'dept_1', team nodes are just numbers
        if (!String(nodeId).startsWith('dept_')) {
            window.location.href = '/teams/' + nodeId + '/';
        }
    });
};

// Start the process when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // The path must match your organization/urls.py prefix
    const apiEndpoint = '/organization/api/teams-data/';

    fetch(apiEndpoint) 
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            initChart(data);
        })
        .catch(error => {
            console.error('Failed to load organizational chart data:', error);
            document.getElementById('cy').innerHTML = 
                `<p style="color:red; padding:20px;">Error loading chart: ${error.message}</p>`;
        });
});