const initChart = (data) => {
    var cy = cytoscape({
        container: document.getElementById('cy'),
        elements: data, // This will be the JSON from your Django view
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'background-color': '#00558E',
                    'color': '#333',
                    'font-size': '12px'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#ccc',
                    'target-arrow-shape': 'triangle', // Your requested arrowhead
                    'target-arrow-color': '#ccc',
                    'curve-style': 'bezier'
                }
            }
        ],
        layout: {
            name: 'cise',
            clusters: function(node) { return node.data('parent'); },
            animate: true
        }
    });
};

// Start the process
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/teams-data/') 
        .then(response => response.json())
        .then(data => initChart(data));
});