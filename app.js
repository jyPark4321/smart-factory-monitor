const express = require('express');
const app = express();

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

app.use(express.static(path.join(__dirname, 'public')));

app.get('/data', function(req, res) {
  // SQLite DB 파일 읽기
  const dbPath = path.join(__dirname, 'data', 'database.db');
  const db = new sqlite3.Database(dbPath);

  const query = req.query.query;

  // 데이터 쿼리
  db.all(query, function(err, rows) {
    if (err) {
      // 에러 처리
      console.error(err);
      res.status(500).send('Internal Server Error');
    } else {
      // 데이터 전송
      res.send(rows);
    }
  });

  // DB 연결 종료
  db.close();
});

const port = 3000;
app.listen(port, () => {
  console.log(`웹 서버가 http://localhost:${port} 에서 실행 중입니다.`);
});
