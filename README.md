# English Reading Class App [![Open App](https://img.shields.io/badge/Open%20App-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://myproject-jm.streamlit.app/)

## Project Description

**English Reading Class App** is a customized Streamlit-based learning application designed for a first-year high school English reading class. The app supports vocabulary learning, active reading, sentence-level highlighting, individual reflection, group discussion, and whole-class sharing. It was developed for a lesson on **Lesson 4: The Winds of Change**, which focuses on how powerful photographs can influence public awareness and bring about social change.

The app is designed to support a classroom model in which students first learn key vocabulary, explore the reading passage individually, open and discuss class-wide highlights in groups, and finally share refined interpretations with teacher feedback.

**Live App:** [https://myproject-jm.streamlit.app/](https://myproject-jm.streamlit.app/)

---

## Teaching Context

### Learners

The target learners are **first-year high school students** studying English as a foreign language. They are preparing for reading-focused English classes in a Korean high school context, where reading comprehension, vocabulary knowledge, and text analysis are important parts of classroom learning and assessment.

### Classroom Environment

The classroom is mainly organized around **English reading instruction**. Students often work individually first and then move into pair or group discussion. The lesson can be implemented in either individual or group settings depending on the teacher’s instructional goals.

### Learner Challenges

Students may have limited opportunities to engage in active reading. In a reading-focused and exam-oriented classroom, lessons can easily become teacher-centered, with students passively receiving explanations. In addition, differences in English proficiency and learning conditions can lead to gaps in comprehension, vocabulary learning, and access to key content knowledge. Therefore, the lesson needs to support both learner-centered exploration and fair delivery of essential knowledge.

---

## Lesson Purpose

This lesson teaches **vocabulary and reading comprehension** through the topic **“The Winds of Change.”** Students read a passage about photographs that contributed to major social changes, including the image of the burning Cuyahoga River and its impact on environmental awareness.

The lesson is meaningful because it allows students to actively investigate the passage while still ensuring that important vocabulary, main ideas, details, and grammar points are shared fairly across the class. Students are not only asked to understand the passage but also to mark important sentences, explain their reasoning, compare ideas with others, and participate in a shared class interpretation.

---

## App Purpose

I built this app to support a high school English reading class where reading takes up a large portion of instruction and assessment. In a college entrance exam-oriented context, students need to understand reading passages accurately, but the classroom should not rely only on one-way teacher explanation. At the same time, it is important that differences in students’ English proficiency do not prevent them from accessing key content.

The app addresses the need for:

- Individual vocabulary learning
- Active and exploratory reading
- Sentence-level reading strategy practice
- Equal access to key reading points
- Peer discussion based on visible evidence
- Teacher feedback based on student responses

The app helps students think first on their own, participate in discussion, and then compare their interpretations with the whole class.

---

## App Design

The app has three main sections:

### 1. Home

The home screen introduces the class with the title **Daea High School English Reading Class** and a simple visual design. It functions as the entry point for the lesson.

### 2. Word

The **Word** section supports class vocabulary practice and individualized vocabulary review.

Before reading the main passage, the teacher presents key vocabulary from the text through teacher-controlled word cards. Students first see only the target word and are given time to think about its meaning. This short thinking time encourages students to activate prior knowledge and notice what they already know or do not know.

When the teacher flips the card, students can check the Korean meaning and the English definition or example information. After checking the answer, each student responds individually by selecting one of two buttons:

- **I Know It**
- **Save to My Words**

If students feel that a word is difficult or unfamiliar, they can save it to **My Words**. These saved words become a personal vocabulary review list that students can revisit after class. After memorizing or reviewing a saved word, students can remove it from their personal list by clicking **Remove**. In this way, the app supports vocabulary learning before, during, and after the lesson.

### 3. Reading

The **Reading** section presents the reading passage and questions directly from the code. Students read the passage sentence by sentence and select a tag for each sentence. The tag categories include:

- Main idea
- Evidence for questions
- Grammar/structure
- I do not understand

When students choose a tag, the sentence is highlighted in a different color according to the selected category. Students can also write a short opinion, question, or reason next to the sentence.

The Reading section follows a staged process. First, students explore the text individually by tagging and highlighting sentences. Then, the teacher opens the full class highlights, and students use those shared results during group discussion. In groups, they compare their own choices with class-wide patterns, discuss differences, and refine their interpretations. Finally, the class shares key findings and receives teacher feedback.

---

## Data and Content

The app currently uses:

- Vocabulary from **Lesson 4: The Winds of Change**
- Reading text about photographs, the Cuyahoga River fire, environmental awareness, Earth Day, and the Clean Water Act
- Reading questions connected to the passage
- Student-generated data such as vocabulary responses, saved words, reading tags, highlights, and comments

The app stores classroom activity data using a local SQLite database.

---

## Classroom Use

The app is used in the lesson in the following sequence:

1. Students learn and review key vocabulary through the Word section.
2. Students save unfamiliar vocabulary to My Words for later individual review.
3. Students read the passage individually in the Reading section.
4. Students tag and highlight sentences according to reading purpose, evidence, grammar, or difficulty.
5. The teacher opens class-wide highlights, and students discuss the shared results in pairs or groups.
6. Students refine their interpretations through group discussion.
7. The class shares final learning products and receives teacher feedback.

This process improves the lesson by making students’ reading processes visible. It also helps the teacher identify which sentences students find important, confusing, or useful as evidence.

---

## How the App Supports Adaptive Learning

The app supports adaptive learning in two main ways.

First, students can save unknown or difficult vocabulary to **My Words**, which creates a personalized vocabulary review list. Students do not need to study the same words in the same way; instead, they can focus on words they personally need to review. After reviewing and memorizing the words, students can remove them from their list, which gives them a simple way to manage their own vocabulary learning progress.

Second, the Reading section allows students to mark sentences based on their own understanding. Students can identify main ideas, supporting evidence, grammar points, and confusing sentences. This supports active reading and allows students with different proficiency levels to participate meaningfully. When the teacher shares the class results, all learners can access important knowledge and compare their interpretations with others.

---

## Teacher Role

The teacher acts as both a **facilitator** and a **knowledge provider**. The teacher controls vocabulary cards, monitors student responses, supports group discussion, shares class highlights, and gives feedback on key reading points. The app helps the teacher balance student-centered exploration with clear instruction.

---

## Limitations

The current version has several limitations:

- The Reading section may not run smoothly on some mobile phones.
- The readability of the Reading section can be improved further, especially on small screens.
- The app currently uses a local SQLite database, so long-term data storage may be limited depending on the deployment environment.
- The reading content and vocabulary are currently managed through code, so non-technical teachers may need support when updating materials.
- More detailed analytics could be added to better track student progress.

---

## Future Development

Future improvements could include:

- Improving mobile compatibility for the Reading section
- Enhancing readability on smaller screens
- Adding an easier teacher interface for changing reading texts and questions
- Supporting export of student responses
- Adding more detailed learning analytics
- Allowing different reading passages and vocabulary sets to be selected by lesson
- Improving long-term data storage using Google Sheets, Supabase, or another external database

---

## Running the App

Open the deployed app here:

[https://myproject-jm.streamlit.app/](https://myproject-jm.streamlit.app/)

To run the app locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Main files:

- `app.py`: Main app structure and navigation
- `flip_recall.py`: Vocabulary learning section
- `text_spotlight.py`: Reading, highlighting, tagging, and sharing section
- `db.py`: Database functions
- `requirements.txt`: Required packages
- `home_student.png`: Home screen image
