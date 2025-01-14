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
// Fonction générique pour générer les graphiques en secteurs
function generatePieChart(dataCount, chartId, containerId, titlePrefix) {
    let modifiedLabels = [];
    let modifiedSizes = [];
    let otherSize = 0;
    let otherSources = []; // Tableau pour stocker les sources groupées dans "Autres"
    
    // Calculer le nombre total de documents
    const totalDocuments = Object.values(dataCount).reduce((sum, value) => sum + value, 0);

    // Regrouper dans "Autres" si plus de 15 documents
    const shouldGroupOthers = totalDocuments > 15;

    Object.entries(dataCount).forEach(([label, size]) => {
        if (shouldGroupOthers && size <= 2) {
            otherSize += size;
            otherSources.push(label);
        } else {
            modifiedLabels.push(label);
            modifiedSizes.push(size);
        }
    });

    if (otherSize > 0 && shouldGroupOthers) {
        modifiedLabels.push('Other (2 or less documents)');
        modifiedSizes.push(otherSize);
    }

    const titleText = `${titlePrefix} ${totalDocuments} documents`;

    const pieData = [{
        type: 'pie',
        values: modifiedSizes,
        labels: modifiedLabels,
        textinfo: 'value',
        hoverinfo: 'label+value',  // Affiche l'étiquette et la valeur dans l'info-bulle
        automargin: true
    }];

    const layout = {
        title: titleText,
        height: 300,
        width: '100%',
        margin: {
            l: 10,
            r: 10,
            t: 50,
            b: 10
        },
        showlegend: false,
        hoverlabel: {
            bgcolor: 'rgba(255, 255, 255, 0.8)',  // Fond blanc semi-transparent
            font: {
                size: 14,  // Ajuste la taille de la police
                family: 'Arial, sans-serif',  // Police de l'info-bulle
            },
            align: 'center',  // Aligne le texte au centre
            namelength: -1,  // Permet de ne pas couper le texte du label
            borderpad: 10,   // Ajoute un espacement intérieur pour l'info-bulle
        },
    };

    Plotly.newPlot(chartId, pieData, layout).then(() => {
        const pieChart = document.getElementById(chartId);
        pieChart.on('plotly_click', function(eventData) {
            const clickedLabel = eventData.points[0].label;
            if (clickedLabel === 'Other (2 or less documents)') {
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
