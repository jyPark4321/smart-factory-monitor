function startDBPreprocessing() {

    // const startDate = document.getElementById('startdate').value;
    // const endDate = document.getElementById('enddate').value;
    const startDate = '2021-01-01';
    const endDate = 2021-12-31;
  
    const xhr = new XMLHttpRequest();
    const url = '/start-db-preprocessing';
    const params = 'start='+startDate+'&end='+endDate;  // 매개변수를 query string 형식으로 생성
    
    // 요청 완료 핸들러 설정
    xhr.onreadystatechange = function() {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            alert('DB 전처리 작업이 완료되었습니다.');
          } else {
            alert('DB 전처리 작업을 시작할 수 없습니다.');
        }
      }
    };
    
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    alert('DB 전처리 작업 요청이 완료되었습니다.');
  
    // 요청 전송
    xhr.send(params);
}
const button = document.getElementById('request_button')
button.addEventListener('click', startDBPreprocessing)