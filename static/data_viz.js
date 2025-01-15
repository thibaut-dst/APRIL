// Function to create pie chart for location
function createPieChartLocation(documents) {
    try {
        const locationCount = {};
        documents.forEach(doc => {
            const location = doc['localisation of scraping'];
            console.log(location);  // Affichera la valeur du champ "localisation of scraping"

            locationCount[location] = (locationCount[location] || 0) + 1;
        });

        generatePieChart(locationCount, 'pie-chart-location', 'other-sources-container-location', 'Locations');
    } catch (error) {
        console.error('Error rendering location pie chart:', error);
        document.getElementById('pie-chart-container-location').innerHTML += '<p>Error loading pie chart location.</p>';
    }
}

// Function to create pie chart for domain
function createPieChartDomain(documents) {
    try {
        const domainCount = {};
        documents.forEach(doc => {
            const domain = doc['domain'];
            domainCount[domain] = (domainCount[domain] || 0) + 1;
        });

        generatePieChart(domainCount, 'pie-chart-domain', 'other-sources-container-domain', 'Domains');
    } catch (error) {
        console.error('Error rendering domain pie chart:', error);
        document.getElementById('pie-chart-container-domain').innerHTML += '<p>Error loading pie chart domain.</p>';
    }
}

// Generic function to generate pie charts
function generatePieChart(dataCount, chartId, containerId, titlePrefix) {
    let modifiedLabels = [];
    let modifiedSizes = [];
    let otherSize = 0;
    let otherSources = []; // Sources groupées dans "Other"
    
    // Calculer le nombre total de domaines ou de localisations distincts
    const distinctCount = Object.keys(dataCount).length; // Nombre de clés uniques
    
    // Trier les labels par taille décroissante
    const sortedData = Object.entries(dataCount).sort((a, b) => b[1] - a[1]);

    // Si moins ou égal à 10 sources, tout afficher
    if (sortedData.length <= 10) {
        sortedData.forEach(([label, size]) => {
            modifiedLabels.push(label);
            modifiedSizes.push(size);
        });
    } else {
        // Afficher les 10 premières sources avec le count le plus élevé
        sortedData.slice(0, 10).forEach(([label, size]) => {
            modifiedLabels.push(label);
            modifiedSizes.push(size);
        });

        // Regrouper le reste dans "Other"
        sortedData.slice(10).forEach(([label, size]) => {
            otherSize += size;
            otherSources.push(label);
        });

        if (otherSize > 0) {
            modifiedLabels.push('Other (less frequent sources)');
            modifiedSizes.push(otherSize);
        }
    }

    const titleText = `${titlePrefix} (${distinctCount} different ${titlePrefix.toLowerCase()})`; // Afficher le nombre distincts (domains ou locations)

    const pieData = [{
        type: 'pie',
        values: modifiedSizes,
        labels: modifiedLabels,
        textinfo: 'value',
        hoverinfo: 'label+value',
        automargin: true
    }];

    const layout = {
        title: titleText,
        height: Math.min(250 + distinctCount * 0.05, 500), // Ajuster la hauteur pour plus de flexibilité
        width: 500, // Réduire la largeur du graphique
        margin: {
            l: 10,
            r: 10,
            t: 50,
            b: 10
        },
        showlegend: false, // N'affiche pas la légende
        hoverlabel: {
            bgcolor: 'rgba(255, 255, 255, 0.8)',
            font: {
                size: 12, // Réduire la taille du texte
                family: 'Arial, sans-serif',
            },
            align: 'center',
            namelength: -1,
            borderpad: 10,
        },
    };

    Plotly.newPlot(chartId, pieData, layout).then(() => {
        const pieChart = document.getElementById(chartId);
        pieChart.on('plotly_click', function(eventData) {
            const clickedLabel = eventData.points[0].label;
            if (clickedLabel === 'Other (less frequent sources)') {
                displayOtherSources(otherSources, containerId);
            }
        });
    });
}

// Function to display the sources in the "Other" section
function displayOtherSources(sources, containerId) {
    const otherSourcesContainer = document.getElementById(containerId);
    otherSourcesContainer.style.display = 'block'; // Make the container visible
    otherSourcesContainer.innerHTML = '';  // Clear any previous content

    if (sources.length === 0) {
        otherSourcesContainer.innerHTML = '<p>No sources in "Other".</p>';
    } else {
        const list = document.createElement('ul');
        sources.forEach(source => {
            const listItem = document.createElement('li');
            listItem.textContent = source;
            list.appendChild(listItem);
        });

        otherSourcesContainer.appendChild(list);
    }
}
