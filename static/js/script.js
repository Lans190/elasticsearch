document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('load-data').addEventListener('click', function() {
        fetch('/load-data')
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerText = data.message;
            })
            .catch(error => console.error('Error:', error));
    });

    document.getElementById('search-data').addEventListener('click', function() {
        const query = document.getElementById('search-query').value;
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const resultsContainer = document.getElementById('search-results');
                resultsContainer.innerHTML = ''; // Clear previous results
                if (data.error) {
                    resultsContainer.innerText = data.error;
                } else {
                    data.forEach(result => {
                        const resultDiv = document.createElement('div');
                        resultDiv.innerHTML = `
                            <p><strong>Home Team:</strong> ${result._source.homeTeam.name}</p>
                            <p><strong>Away Team:</strong> ${result._source.awayTeam.name}</p>
                            <p><strong>Score:</strong> ${result._source.score.fullTime.home} - ${result._source.score.fullTime.away}</p>
                            <p><strong>Date:</strong> ${result._source.utcDate}</p>
                            <hr>
                        `;
                        resultsContainer.appendChild(resultDiv);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    });
});
