// Функция для установки одинаковой ширины ячеек в колонках
function setEqualColumnWidths() {
    const sections = document.querySelectorAll('.section_oper_wr');
    
    sections.forEach(section => {
        // Получаем все oper_account внутри section_oper_wr
        const operAccounts = section.querySelectorAll('.oper_account');
        if (!operAccounts.length) return;

        // Получаем все строки из всех oper_account
        const allRows = Array.from(operAccounts).flatMap(account => 
            Array.from(account.querySelectorAll('.oper-account-row'))
        );
        if (!allRows.length) return;

        // Получаем все ячейки месяца и значения из первой строки первого oper_account
        const monthCells = Array.from(operAccounts[0].querySelector('.oper-account-row').querySelectorAll('.oper-account-month, .oper-account-value'));
        
        // Для каждой колонки месяца
        monthCells.forEach((_, columnIndex) => {
            let maxWidth = 0;
            
            // Находим максимальную ширину в колонке среди всех строк всех oper_account
            allRows.forEach(row => {
                const cells = row.querySelectorAll('.oper-account-month, .oper-account-value');
                if (cells[columnIndex]) {
                    const cell = cells[columnIndex];
                    const cellWidth = cell.scrollWidth;
                    maxWidth = Math.max(maxWidth, cellWidth);
                }
            });
            
            // Устанавливаем найденную максимальную ширину для всех ячеек в колонке
            allRows.forEach(row => {
                const cells = row.querySelectorAll('.oper-account-month, .oper-account-value');
                if (cells[columnIndex]) {
                    cells[columnIndex].style.width = `${maxWidth}px`;
                }
            });
        });
    });
}

// Вызываем функцию при загрузке страницы
document.addEventListener('DOMContentLoaded', setEqualColumnWidths);

// Вызываем функцию при изменении размера окна
window.addEventListener('resize', setEqualColumnWidths);

// Вызываем функцию после загрузки всех ресурсов
window.addEventListener('load', setEqualColumnWidths); 