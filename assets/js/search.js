// في main.js أو search.js
const searchInput = document.querySelector('.search-input');
const resultsContainer = document.createElement('div');
resultsContainer.classList.add('search-results');
document.querySelector('.search-info').after(resultsContainer); // إدراج بعد قسم البحث

searchInput.addEventListener('input', (e) => {
  const query = e.target.value.toLowerCase();
  resultsContainer.innerHTML = ''; // مسح النتائج السابقة
  if (query) {
    const filteredBooks = libraryBooks.filter(book => 
      book.title_ar.toLowerCase().includes(query) || 
      book.title_en.toLowerCase().includes(query) ||
      book.metadata.keywords.some(keyword => keyword.toLowerCase().includes(query))
    );
    if (filteredBooks.length === 0) {
      resultsContainer.innerHTML = '<div class="no-results">لم يتم العثور على كتب تطابق بحثك. حاول استخدام مصطلحات أخرى.</div>';
    } else {
      filteredBooks.forEach(book => {
        const resultDiv = document.createElement('div');
        resultDiv.classList.add('book-search-result');
        resultDiv.innerHTML = `
          <div class="book-result-header">
            <img class="book-result-cover" src="${book.links.ar.cover || book.links.en.cover}" alt="${book.title_ar}" loading="lazy">
            <div class="book-result-info">
              <h3>${book.title_ar}</h3>
              <p class="book-meta">تأليف: ${book.metadata.author}</p>
              <p class="book-desc">${getBookDescription(book.id)}</p>
            </div>
          </div>
        `;
        resultsContainer.appendChild(resultDiv);
      });
    }
  }
});
