const sqlite3 = require('sqlite3').verbose();
const dbPath = '../data/database.db';

// 데이터베이스 연결
const db = new sqlite3.Database(dbPath);

// 쿼리 실행
db.serialize(() => {
  db.all('SELECT * FROM data_output ORDER BY date DESC LIMIT 1', (err, rows) => {
    if (err) {
      console.error(err.message);
      return;
    }
    
    // 결과 출력
    rows.forEach((row) => {
      console.log(row);
    });
  });
});

// 데이터베이스 연결 종료
db.close();