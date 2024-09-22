const puppeteer = require("puppeteer.")

async function rmp(){
    //Loads Rate My Professor Rutgers Page
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto("https://www.ratemyprofessors.com/school/825");
}

async function classList(){
    //Loads Rutgers Schedule of Classes
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto("https://classes.rutgers.edu/soc/#home");
}