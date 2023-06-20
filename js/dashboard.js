console.log('dashboard.js start');
// SQLite 데이터베이스 파일 로드
const xhr = new XMLHttpRequest();
xhr.open('GET', './data/database.db', true);
console.log('db open');
xhr.responseType = 'arraybuffer';
xhr.onload = function () {
    const data = new Uint8Array(xhr.response);
    const db = new SQL.Database(data);

    // 데이터베이스 쿼리 실행
    const query = 'SELECT * FROM data_output ORDER BY created_at DESC LIMIT 1';
    const result = db.exec(query);
    const row = result[0].values[0];

    // 결과 처리
    console.log(row);

    // 데이터베이스 연결 종료
    db.close();
};