import csv
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

type_map = {
    'A': 'Ability & Aptitude',
    'B': 'Biodata & Situational Judgement',
    'C': 'Competencies',
    'D': 'Development & 360',
    'E': 'Assessment Exercises',
    'K': 'Knowledge & Skills',
    'P': 'Personality & Behavior',
    'S': 'Simulations'
}

async def extract_detail_data(context, url, basic_info):
    try:
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("h1")
        basic_info["Name"] = title.text.strip() if title else basic_info["Name"]

        def get_text(label):
            tag = soup.find("h4", string=label)
            return tag.find_next_sibling("p").text.strip() if tag else ""

        basic_info.update({
            "Description": get_text("Description"),
            "Job Levels": get_text("Job levels"),
            "Languages": get_text("Languages"),
            "Duration": get_text("Assessment length"),
        })
    except:
        pass
    finally:
        await page.close()
        return basic_info

async def process_table_rows(context, rows, base_url, solution_type):
    tasks = []

    for row in rows:
        link_tag = row.select_one("td a")
        if not link_tag:
            continue

        name = link_tag.text.strip()
        href = link_tag["href"]
        url = base_url + href if href.startswith("/") else href

        cells = row.select("td")
        remote_testing = "Yes" if len(cells) > 1 and cells[1].select_one(".checkmark-green, .catalogue__circle.-yes, span.yes") else "No"
        adaptive_irt = "Yes" if len(cells) > 2 and cells[2].select_one(".checkmark-green, .catalogue__circle.-yes, span.yes") else "No"

        test_type_cell = cells[3] if len(cells) > 3 else None
        test_types = ""

        if test_type_cell:
            type_indicators = test_type_cell.select("span.product-catalogue__key")
            if type_indicators:
                raw_types = [s.text.strip() for s in type_indicators]
                test_types = ", ".join(type_map.get(t, t) for t in raw_types)
            else:
                test_types = test_type_cell.get_text().strip()

        basic_info = {
            "Name": name,
            "URL": url,
            "Remote Testing": remote_testing,
            "Adaptive/IRT": adaptive_irt,
            "Duration": "",
            "Test Types": test_types,
            "Description": "",
            "Job Levels": "",
            "Languages": "",
            "Solution Type": solution_type
        }

        tasks.append(extract_detail_data(context, url, basic_info))

    return await asyncio.gather(*tasks) if tasks else []

async def scrape_all_pages_for_table(context, page, table_index, solution_type, start_url):
    all_results = []
    current_url = start_url
    visited_urls = set()
    base_url = "https://www.shl.com"

    while current_url and current_url not in visited_urls:
        visited_urls.add(current_url)

        try:
            await page.goto(current_url)
            await page.wait_for_load_state("networkidle")
        except:
            break

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        table_wrappers = soup.select("div.custom__table-wrapper, div.custom_table-wrapper")

        if table_index >= len(table_wrappers):
            break

        table_wrapper = table_wrappers[table_index]
        table = table_wrapper.select_one("table")
        if not table:
            break

        rows = table.select("tbody tr")
        results = await process_table_rows(context, rows, base_url, solution_type)
        all_results.extend(results)

        pagination = table_wrapper.find_next_sibling("ul", class_="pagination")
        if not pagination:
            all_paginations = soup.select("ul.pagination")
            if table_index < len(all_paginations):
                pagination = all_paginations[table_index]

        next_page_url = None
        if pagination:
            next_link = pagination.select_one("li.-next:not(.-disabled) a, li.next:not(.disabled) a, a.next:not(.disabled)")
            if next_link and next_link.get("href"):
                href = next_link.get("href")
                next_page_url = base_url + href if href.startswith("/") else href

        if next_page_url and next_page_url not in visited_urls:
            current_url = next_page_url
        else:
            break

    return all_results

async def scrape_shl_catalog_async():
    all_results = []
    start_url = "https://www.shl.com/solutions/products/product-catalog/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        pre_packaged_results = await scrape_all_pages_for_table(
            context, page, table_index=0, solution_type="Pre-packaged Job Solutions", start_url=start_url
        )
        all_results.extend(pre_packaged_results)

        individual_start_url = "https://www.shl.com/products/product-catalog/?type=1"
        individual_results = await scrape_all_pages_for_table(
            context, page, table_index=0, solution_type="Individual Test Solutions", start_url=individual_start_url
        )
        all_results.extend(individual_results)

        await browser.close()

    return all_results

def clean_field(value):
    if isinstance(value, str):
        return value.replace('\r', ' ').replace('\n', ' ').strip()
    return value

def export_to_csv(data, filename="shl_full_catalog.csv"):
    if not data:
        return

    def write_csv(file_path, dataset):
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = list(dataset[0].keys())
            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
                quoting=csv.QUOTE_ALL
            )
            writer.writeheader()
            for item in dataset:
                cleaned_item = {k: clean_field(v) for k, v in item.items()}
                writer.writerow(cleaned_item)

    pre_packaged = [item for item in data if item.get("Solution Type") == "Pre-packaged Job Solutions"]
    individual = [item for item in data if item.get("Solution Type") == "Individual Test Solutions"]

    write_csv(filename, data)
    if pre_packaged:
        write_csv("pre_packaged_solutions.csv", pre_packaged)
    if individual:
        write_csv("individual_solutions.csv", individual)


if __name__ == "__main__":
    final_data = asyncio.run(scrape_shl_catalog_async())
    export_to_csv(final_data)
