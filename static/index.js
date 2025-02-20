const headline_btn = document.getElementById("headline-btn");
const url_btn = document.getElementById("url-btn");

const box = document.getElementById('url');
const block = document.getElementById('headline');
//// 👇️ removes element from DOM

const item = localStorage.getItem('activeTab');
if (item == "headline") {
    box.style.display= 'none';
    block.style.display = 'block';
    headline_btn.classList.add("active");
    url_btn.classList.remove("active");
} else {
    box.style.display= 'block';
    block.style.display = 'none';
    headline_btn.classList.remove("active");
    url_btn.classList.add("active");
}

headline_btn.addEventListener('click', () => {
  localStorage.setItem("activeTab", "headline");
  headline_btn.classList.add("active");
  url_btn.classList.remove("active");
  console.log("Clicked headline btn");
  const box = document.getElementById('url');
  const block = document.getElementById('headline');
  // 👇️ removes element from DOM
  box.style.display = 'none';
  block.style.display = 'block';
  // 👇️ hides element (still takes up space on page)
  // box.style.visibility = 'hidden';
});



url_btn.addEventListener('click', () => {
  localStorage.setItem("activeTab", "url");
  console.log("Clicked url btn");
  headline_btn.classList.remove("active");
  url_btn.classList.add("active");
  const box = document.getElementById('headline');
  const block = document.getElementById('url');
  // 👇️ removes element from DOM
  box.style.display = 'none';
  block.style.display = 'block';
  // 👇️ hides element (still takes up space on page)
  // box.style.visibility = 'hidden';
});