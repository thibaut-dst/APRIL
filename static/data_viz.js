document.addEventListener("DOMContentLoaded", async function () {
    try {
        // Fetch data from the backend endpoint
        const response = await fetch('/api/piechart');
        if (!response.ok) throw new Error('Failed to fetch data');

        const data = await response.json();

        // Check if the response contains the required data
        if (data.labels && data.sizes) {

            // Modify the labels and sizes to group values equal to 1 as "Other"
            let modifiedLabels = [];
            let modifiedSizes = [];
            let otherSize = 0;

            // Loop through the data and modify it
            data.labels.forEach((label, index) => {
                if (data.sizes[index] <= 2) {
                    // Add the size to 'otherSize' and skip adding it as a separate slice
                    otherSize += data.sizes[index];
                } else {
                    // Add normal data
                    modifiedLabels.push(label);
                    modifiedSizes.push(data.sizes[index]);
                }
            });

            // If there's any value to group into "Other", add it as a new slice
            if (otherSize > 0) {
                modifiedLabels.push('Other');
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
                textinfo: 'none', // Disable labels inside or outside the chart
                automargin: true,
                marker: { line: { color: 'black', width: 1 } }
            }];

            // Define the layout for the pie chart
            const layout = {
                title: titleText,
                height: 350,
                width: '100%',
                showlegend: false,
                legend: {
                    title: { text: "Sources" },
                    x: 1,
                    y: 0.5,
                    font: { size: 12 },
                    orientation: 'v'
                }
            };

            // Render the pie chart inside the #pie-chart div
            Plotly.newPlot('pie-chart', pieData, layout);
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
