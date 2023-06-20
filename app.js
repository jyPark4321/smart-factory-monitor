const express = require('express');
const app = express();
const { exec } = require('child_process');
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

app.post('/start-db-preprocessing', function(req, res) {

  const pythonScriptPath = 'data/processData.py';
  const startDate = req.body.startDate;
  const endDate = req.body.endDate;

  console.log("전처리 시작")
  const command = `python ${pythonScriptPath} ${startDate} ${endDate}`;
  
  exec('python data/processData.py', (error, stdout, stderr) => {
    if (error) {
      console.error(`파이썬 코드 실행 중 오류 발생: ${error}`);
      res.sendStatus(0);
      return;
    }
    // stdout에서 파이썬 코드 실행 결과를 처리
    console.log(`전처리 작업 요청에 성공하였습니다.`);
  });
  res.sendStatus(200);
});