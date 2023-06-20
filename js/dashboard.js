const sqlite3 = require('sqlite3').verbose();
const dbPath = '../data/database.db';

// 데이터베이스 연결
const db = new sqlite3.Database(dbPath);

// 쿼리 실행
db.serialize(() => {
  db.all('SELECT * FROM data_output ORDER BY date DESC LIMIT 1', (err, row) => {
    if (err) {
      console.error(err.message);
      return;
    }

    const sol = JSON.parse(row[0].sol);
    console.log(sol['(item, machine, time)']);  
    var data = [];
    sol.forEach((sol => {
        console.log(sol)
        data.push( {
            "품목": sol['(item, machine, time)'][0],
            "기계 번호": sol['(item, machine, time)'][1],
            "주문 일자": sol['(item, machine, time)'][2],
            "수량": sol.qty
        });
    }))
    var $table = $('#datatablesDashboard')
    $table.bootstrapTable({ data: data })
  });
});

// 데이터베이스 연결 종료
db.close();