# Assignment 1 Requirements — AI Application Example I (Search/Optimisation Problem)

> Restructured from the original subject-outline text for quick reference. Original wording preserved where it matters (dates, weighting, submission rules); reorganized by theme.

## 1. Overview

| Item | Detail |
|---|---|
| Assessment | Task 1 of 3 — "Mini AI application examples" |
| This example | **Example I**: a navigational search problem OR a local search / optimisation problem |
| Learning outcome | SLO2, course outcome D.1 |
| Weighting | 45% total across all 3 examples (this is 1 of 3 deliverable pairs) |
| Due date | **Friday, Week 6, 11:59 PM** |

## 2. What Problem to Solve

Choose **one** of the following (your own real-world-inspired problem, simplified):

- **Navigational / path-finding search problem** — options:
  - (i) An intelligent warehouse robot that navigates to pick ordered products (cf. Amazon robotic warehouses).
  - (ii) An intelligent agent guiding people through a geographic region — e.g., pick ~20 real locations in your local area (use Google Maps for coordinates), build a graph similar to the classic "Romania problem."
- **Local search / optimisation problem** — e.g., a Travelling Salesman Problem: pick ~20 places you want to visit (e.g., travel destinations), map them via Google Maps, and find the optimal visiting sequence that minimizes cost.

## 3. Core Technical Requirement

- Solve the chosen problem using **two different AI techniques** covered in the labs.
- Both must be genuinely **working solutions** (not just one implemented well and one token attempt).
- **Compare** the two techniques' results (e.g., solution quality, efficiency, path cost).
- **Recommend** which technique is better for this specific problem, with justification.

## 4. Deliverables (2 files to submit)

### A. Professional Report
- Use the provided report template; follow its section instructions, then remove the instructions before submitting.
- **Must include a link to the Colab notebook on the cover page.**
- **Length: 10–12 standard A4 pages** (standard margins/font/line spacing), **excluding** references, cover page, table of contents, and summary.
- Format: `.docx` or `.pdf`.

### B. Working Notebook
- Must run in **Google Colab**.
- **Annotations required**: a markdown/text cell above each code cell explaining it in **your own words**.
  - ⚠️ Do not copy annotations from lab materials or other sources — you may use lab material as a reference, but wording must be original. Penalized if not.
- **Outputs must be recorded/visible in the notebook itself** (not require the marker to re-run it). Must show:
  1. The components of the problem (states, actions, graph/search space, etc.)
  2. Key parameters used in each AI technique
  3. Performance metrics of each technique
  4. Results when the model/technique is applied to future/new data
- No length limit.
- Submit as a **PDF printout** of the notebook (in addition to the live Colab link in the report).

## 5. Submission Checklist

- [ ] Report (.docx or .pdf), 10–12 pages, template followed, Colab link on cover page
- [ ] Notebook PDF printout, with own-words annotations and recorded outputs
- [ ] Both files uploaded to the correct Assignments folder
- [ ] References checked against the referencing guide

## 6. Other Rules / Notes

- **Late penalty** applies unless: 3-day extension granted, special consideration approved before due date, or subject coordinator approved a late submission before due date.
- Projects with a **user-friendly interface** are eligible for the FEIT AI Showcase (optional, not required for grading).
- Feedback returned via marking-sheet rubric ranks, 2–4 weeks after the due date.

## 7. Open Decisions to Make (for brainstorming/planning)

- [ ] Which problem type: path-finding vs. optimisation (TSP-style)?
- [ ] What's the concrete scenario (warehouse robot / regional navigation / travel destinations)?
- [ ] Which 2 AI techniques (from labs) to compare — e.g., uninformed search (BFS/DFS/UCS) vs. informed search (A*/Greedy) for path-finding; or hill-climbing vs. simulated annealing / genetic algorithm for optimisation?
- [ ] Data source for the ~20 locations (Google Maps coordinates)?
