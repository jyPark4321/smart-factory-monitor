const query = 'SELECT * FROM data_output ORDER BY date DESC LIMIT 1';
const url = '/data?query=' + encodeURIComponent(query);

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log(data);
    const tableBody = document.getElementById('datatablesDashboard').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';

    const sol = JSON.parse(data[0].sol);
    var sol_ = [];
    console.log(sol['(item, machine, time)']);
    for (const index in sol.qty) {
      sol_ = sol['(item, machine, time)'][index]

      const insert_row = tableBody.insertRow();
      const itemCell = insert_row.insertCell();
      const machineCell = insert_row.insertCell();
      const timeCell = insert_row.insertCell();
      const qtyCell = insert_row.insertCell();

      itemCell.textContent = sol_[0];
      machineCell.textContent = sol_[1];
      timeCell.textContent = sol_[2];
      qtyCell.textContent = sol.qty[index];
    }
  })
  .catch(error => {
    console.error('오류 발생:', error);
  });
