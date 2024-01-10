document.querySelectorAll('#navbar-example2>[data-bs-toggle="tab"]').forEach(el => {
    el.addEventListener('shown.bs.tab', () => {
        const target = el.getAttribute('data-bs-target');
        const scrollElem = document.querySelector(`${target} [data-bs-spy="scroll"]`);
        bootstrap.ScrollSpy.getOrCreateInstance(scrollElem).refresh();
    });
});

const scrollSpy = new bootstrap.ScrollSpy(document.body, {
    target: '#navbar-example2'
});

document.getElementById('navbarDropdown').addEventListener('click', function () {
    var dropdown = new bootstrap.Dropdown(this);
  
    // 使用 toggle 方法切换下拉菜单的状态
    dropdown.toggle();
  });


if (assessmentType === 'deep') {
    dependentsSection.style.display = 'block';
    enableFields(['MentHlth', 'PhysHlth', 'Age', 'Education']);
} else {
    dependentsSection.style.display = 'none';
    disableFields(['MentHlth', 'PhysHlth', 'Age', 'Education']);
}

function enableFields(fields) {
    fields.forEach(function (fieldName) {
        var field = document.getElementById(fieldName);
        if (field) {
            field.removeAttribute('disabled');
        }
    });
}
function disableFields(fields) {
    fields.forEach(function (fieldName) {
        var field = document.getElementById(fieldName);
        if (field) {
            field.setAttribute('disabled', 'disabled');
        }
    });
}