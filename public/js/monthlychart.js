const query = "SELECT MONTH(date_column) AS month, COUNT(*) AS count FROM your_table GROUP BY MONTH(date_column) ORDER BY month";
const url = '/data?query=' + encodeURIComponent(query);

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log(data);

  })
  .catch(error => {
    console.error('오류 발생:', error);
  });
