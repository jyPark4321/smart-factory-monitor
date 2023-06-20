const query = 'SELECT time_range, data FROM data_output ORDER BY date DESC LIMIT 1';
const url = '/data?query=' + encodeURIComponent(query);

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log(data);
    const tableBody = document.getElementById('datatables1').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';

    const data_ = JSON.parse(data[0].data);
    for (const index in data_.urgent) {

      const insert_row = tableBody.insertRow();
      const timeCell = insert_row.insertCell();
      const itemCell = insert_row.insertCell();
      const costCell = insert_row.insertCell();
      const urgentCell = insert_row.insertCell();
      const qtyCell = insert_row.insertCell();
      const machineCell = insert_row.insertCell();
      const capacityCell = insert_row.insertCell();

      timeCell.textContent = data_.time[index];
      itemCell.textContent = data_.item[index];
      costCell.textContent = data_.cost[index];
      urgentCell.textContent = data_.urgent[index];
      qtyCell.textContent = data_.qty[index];
      machineCell.textContent = data_.machine[index];
      capacityCell.textContent = data_.capacity[index];
    }

    const timerange = document.getElementById('processTimeRange');
    const time_range_json = JSON.parse(data[0].time_range);
    timerange.textContent = time_range_json['start_date']+' ~ '+time_range_json['end_date'];

    const datatablesSimple = document.getElementById('datatables1');
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }
  })
  .catch(error => {
    console.error('오류 발생:', error);
  });
