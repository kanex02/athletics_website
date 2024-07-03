function scrollSave(id)
{
    var item = document.getElementById(id);
    item.style.pointerEvents = 'none';
    item.style.background = 'orange'
    var tably = document.querySelector('.student_table_wrapper');
    sessionStorage.setItem('xscroll', tably.scrollLeft);
    sessionStorage.setItem('tyscroll', tably.scrollTop);
}

function lowd()
{
    var tably = document.querySelector('.student_table_wrapper');
    tably.scrollLeft += sessionStorage.getItem('xscroll');
    tably.scrollTop += sessionStorage.getItem('tyscroll');
}

function clearSesh()
{
    sessionStorage.clear();
}

function resetScroll()
{
    sessionStorage.setItem('yscroll', 0);
    sessionStorage.setItem('tyscroll', 0);
    sessionStorage.setItem('xscroll', 0);
}

function printDiv() {
    let divContents = '<h3>BHS Athletics Sign Up'; 

    let formclass = document.getElementById('formclass').value;
    if (formclass != '') {
        divContents += ' - ';
        divContents += formclass;
    }

    divContents += '</h3>';

    divContents += document.getElementById("student_table").outerHTML;

    const frame = document.createElement('iframe');

    frame.setAttribute('id', 'Frame');
    frame.setAttribute('name', 'Frame');
    frame.setAttribute('style', 'display: none;');

    document.body.appendChild(frame);

    let html = '';

    html += '<html>';

    let	headerHtml = '';

    // loop through the styleSheets object and pull in all styles
    for (let i = 0; i < document.styleSheets.length; i++) {
      headerHtml += '<style>';
      
      try {
        for (let j = 0; j < document.styleSheets[i].cssRules.length; j++) {
          headerHtml += document.styleSheets[i].cssRules[j].cssText || '';
        }
      } catch(e) {}
      
      headerHtml += '</style>';
    }

    frame.contentWindow.document.head.innerHTML = headerHtml;

    frame.contentWindow.document.body.innerHTML = divContents;

    frame.contentWindow.print();
}

document.addEventListener('keydown', function (event) {
    if((event.ctrlKey || event.metaKey) && event.key == 'p') {
        event.preventDefault();
        printDiv();
    }
})