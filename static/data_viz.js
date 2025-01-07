document.addEventListener("DOMContentLoaded", async function () {
    try {
        // Fetch data from the backend endpoint
        const response = await fetch('/api/piechart_domain');
        if (!response.ok) throw new Error('Failed to fetch data');

        const data = await response.json();

        // Check if the response contains the required data
        if (data.labels && data.sizes) {

            // Modify the labels and sizes to group values equal to 1 as "Other"
            let modifiedLabels = [];
            let modifiedSizes = [];
            let otherSize = 0;
            let otherSources = []; // Array to store sources grouped into "Other"

            // Loop through the data and modify it
            data.labels.forEach((label, index) => {
                if (data.sizes[index] <= 2) {
                    // Add the size to 'otherSize' and skip adding it as a separate slice
                    otherSize += data.sizes[index];
                    // Add the label to "Other" sources
                    otherSources.push(label);
                } else {
                    // Add normal data
                    modifiedLabels.push(label);
                    modifiedSizes.push(data.sizes[index]);
                }
            });

            // If there's any value to group into "Other", add it as a new slice
            if (otherSize > 0) {
                modifiedLabels.push('Other (2 or less documents)');
                modifiedSizes.push(otherSize);
            }

            // Calculate the total count of documents (sum of sizes)
            const totalDocuments = modifiedSizes.reduce((sum, value) => sum + value, 0);

            // Set the dynamic title with the total count
            const titleText = `Le filtre affiche ${totalDocuments} documents`;

            // Prepare the Plotly data
            const pieData = [{
                type: 'pie',
                values: modifiedSizes,//data.sizes
                labels: modifiedLabels,//data.labels
                textinfo: 'value', // Disable labels inside or outside the chart
                automargin: true
            }];

            // Define the layout for the pie chart
            const layout = {
                title: titleText,
                height: 300,
                width: '100%',
                margin: {
                    l: 10, // Left margin
                    r: 10, // Right margin
                    t: 50, // Top margin
                    b: 10  // Bottom margin
                },
                showlegend: false,
            };


            // Render the pie chart inside the #pie-chart div
            Plotly.newPlot('pie-chart', pieData, layout).then(() => {

            // Event listener for clicking on the pie chart
            const pieChart = document.getElementById('pie-chart');
            pieChart.on('plotly_click', function(eventData) {
                    const clickedLabel = eventData.points[0].label;
                    if (clickedLabel === 'Other') {
                        // Display the sources that were grouped into "Other"
                        displayOtherSources(otherSources);
                    }
                });
            });
        } else {
            // Display an error message if no data is available
            document.getElementById('pie-chart-container').innerHTML += '<p>Pie chart could not be loaded.</p>';
        }
    } catch (error) {
        // Log any errors that occur
        console.error('Error rendering pie chart:', error);
        document.getElementById('pie-chart-container').innerHTML += '<p>Error loading pie chart.</p>';
    }
});

// Function to display the sources in the "Other" section
function displayOtherSources(sources) {
    const otherSourcesContainer = document.getElementById('other-sources-container');
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

        // Append the list to the container
        otherSourcesContainer.appendChild(list);
    }
}
