const libraryBooks = [
    {
        id: "conscious-contemplation",
        title_ar: "نحو تدبر واعٍ",
        title_en: "Towards Conscious Contemplation",
        path_ar: "https://drive.google.com/file/d/1dm_qsNzgCJdZag3a5LJg7_V5Qvobu-vB/view?usp=sharing",
        path_en: "https://drive.google.com/file/d/1Q2w65HUIVr-JE6OEyNoTo5AQ1sMXye1W/view?usp=sharing",
        pdf_ar: "https://dn720702.ca.archive.org/0/items/20250529_20250529_2132/%D9%86%D8%AD%D9%88%20%D8%AA%D8%AF%D8%A8%D8%B1%D9%8D%20%D9%88%D8%A7%D8%B9%D9%8D%20%D8%AF%D9%84%D9%8A%D9%84%20%D8%B9%D9%85%D9%84%D9%8A%20%D9%84%D9%81%D9%87%D9%85%20%D9%88%D8%AA%D8%B7%D8%A8%D9%8A%D9%82%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%20%D8%A7%D9%84%D9%83%D8%B1%D9%8A%D9%85%20%D9%81%D9%8A%20%D8%A7%D9%84%D8%B9%D8%B5%D8%B1%20%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB.pdf",
        pdf_en: "https://ia800602.us.archive.org/9/items/towards-conscious-contemplation-a-practical-guide-to-understanding-and-applying-/TOWARDS%20CONSCIOUS%20CONTEMPLATION%20%20%20A%20PRACTICAL%20GUIDE%20TO%20UNDERSTANDING%20AND%20APPLYING%20THE%20NOBLE%20QUR%27AN%20IN%20THE%20MODERN%20ERA.pdf",
        text_ar: "https://archive.org/stream/20250529_20250529_2132/%D9%86%D8%AD%D9%88%20%D8%AA%D8%AF%D8%A8%D8%B1%D9%8D%20%D9%88%D8%A7%D8%B9%D9%8D%20%D8%AF%D9%84%D9%8A%D9%84%20%D8%B9%D9%85%D9%84%D9%8A%20%D9%84%D9%81%D9%87%D9%85%20%D9%88%D8%AA%D8%B7%D8%A8%D9%8A%D9%82%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%20%D8%A7%D9%84%D9%83%D8%B1%D9%8A%D9%85%20%D9%81%D9%8A%20%D8%A7%D9%84%D8%B9%D8%B5%D8%B1%20%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB_djvu.txt",
        text_en: "https://archive.org/stream/towards-conscious-contemplation-a-practical-guide-to-understanding-and-applying-/TOWARDS%20CONSCIOUS%20CONTEMPLATION%20%20%20A%20PRACTICAL%20GUIDE%20TO%20UNDERSTANDING%20AND%20APPLYING%20THE%20NOBLE%20QUR%27AN%20IN%20THE%20MODERN%20ERA_djvu.txt",
        category: "quranic_studies",
        ai_access: {
            structured_data: true,
            api_accessible: true,
            content_analysis: true,
            formats: ["html", "pdf", "txt"]
        }
    },
    {
        id: "anwar-al-bayan",
        title_ar: "أنوار البيان في رسم المصحف العثماني",
        title_en: "Anwar Al-Bayan in the Drawing of the Ottoman Quran",
        path_ar: "https://drive.google.com/file/d/1xM6KWN0wMorA_WwP5eHDaG77-QHNO9_y/view?usp=sharing",
        path_en: "https://drive.google.com/file/d/10rf76k4G3Wn2zp7e8cv998ZLH_gDQIDU/view?usp=sharing",
        pdf_ar: "https://dn721701.ca.archive.org/0/items/20250529_20250529_2033/%D8%A3%D9%86%D9%88%D8%A7%D8%B1%20%D8%A7%D9%84%D8%A8%D9%8A%D8%A7%D9%86%20%D9%81%D9%8A%20%D8%B1%D8%B3%D9%85%20%D8%A7%D9%84%D9%85%D8%B5%D8%AD%D9%81%20%D8%A7%D9%84%D8%B9%D8%AB%D9%85%D8%A7%D9%86%D9%8A%20%D8%A7%D9%84%D9%83%D8%B4%D9%81%20%D8%B9%D9%86%20%D8%A3%D8%B3%D8%B1%D8%A7%D8%B1%20%D8%A7%D9%84%D9%84%D8%B3%D8%A7%D9%86.pdf",
        pdf_en: "https://dn721503.ca.archive.org/0/items/anwar-al-bayan-in-the-drawing-of-the-ottoman-qur-an-revealing-the-secrets-of-the-tongue/ANWAR%20AL-BAYAN%20IN%20THE%20DRAWING%20OF%20THE%20OTTOMAN%20QUR%27AN%20%20%20REVEALING%20THE%20SECRETS%20OF%20THE%20TONGUE.pdf",
        text_ar: "https://archive.org/stream/20250529_20250529_2033/%D8%A3%D9%86%D9%88%D8%A7%D8%B1%20%D8%A7%D9%84%D8%A8%D9%8A%D8%A7%D9%86%20%D9%81%D9%8A%20%D8%B1%D8%B3%D9%85%20%D8%A7%D9%84%D9%85%D8%B5%D8%AD%D9%81%20%D8%A7%D9%84%D8%B9%D8%AB%D9%85%D8%A7%D9%86%D9%8A%20%D8%A7%D9%84%D9%83%D8%B4%D9%81%20%D8%B9%D9%86%20%D8%A3%D8%B3%D8%B1%D8%A7%D8%B1%20%D8%A7%D9%84%D9%84%D8%B3%D8%A7%D9%86_djvu.txt",
        text_en: "https://archive.org/stream/anwar-al-bayan-in-the-drawing-of-the-ottoman-qur-an-revealing-the-secrets-of-the-tongue/ANWAR%20AL-BAYAN%20IN%20THE%20DRAWING%20OF%20THE%20OTTOMAN%20QUR%27AN%20%20%20REVEALING%20THE%20SECRETS%20OF%20THE%20TONGUE_djvu.txt",
        category: "quranic_studies",
        ai_access: {
            structured_data: true,
            api_accessible: true,
            content_analysis: true,
            formats: ["html", "pdf", "txt"]
        }
    },
    {
        id: "changing-the-concepts",
        title_ar: "تغيير المفاهيم للمصطلحات القرآنية",
        title_en: "Changing the Concepts of Quranic Terminology",
        path_ar: "https://drive.google.com/file/d/1ht_teo2VpDIsZxnQsvByxqLnHXqcEBv9/view?usp=sharing",
        path_en: "https://drive.google.com/file/d/1_4MtnKCy3rsF-f--djCpAiNLxPmGKvDK/view?usp=sharing",
        pdf_ar: "https://ia801709.us.archive.org/33/items/20250529_20250529_2050/%D8%AA%D8%BA%D9%8A%D9%8A%D8%B1%20%D8%A7%D9%84%D9%85%D9%81%D8%A7%D9%87%D9%8A%D9%85%20%D9%84%D9%84%D9%85%D8%B5%D8%B7%D9%84%D8%AD%D8%A7%D8%AA%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%D8%A9%20%D9%83%D8%AA%D8%B7%D8%A8%D9%8A%D9%82%20%D9%84%D9%81%D9%82%D9%87%20%D8%A7%D9%84%D9%84%D8%B3%D8%A7%D9%86%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A.pdf",
        pdf_en: "https://dn721908.ca.archive.org/0/items/changing-the-concepts-of-quranic-terminology-as-an-application-of-the-jurisprude/Changing%20the%20Concepts%20of%20Quranic%20Terminology%20as%20an%20Application%20of%20the%20Jurisprudence%20of%20the%20Qur%27anic%20Tongue.pdf",
        text_ar: "https://archive.org/stream/20250529_20250529_2050/%D8%AA%D8%BA%D9%8A%D9%8A%D8%B1%20%D8%A7%D9%84%D9%85%D9%81%D8%A7%D9%87%D9%8A%D9%85%20%D9%84%D9%84%D9%85%D8%B5%D8%B7%D9%84%D8%AD%D8%A7%D8%AA%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%D8%A9%20%D9%83%D8%AA%D8%B7%D8%A8%D9%8A%D9%82%20%D9%84%D9%81%D9%82%D9%87%20%D8%A7%D9%84%D9%84%D8%B3%D8%A7%D9%86%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A_djvu.txt",
        text_en: "https://archive.org/stream/changing-the-concepts-of-quranic-terminology-as-an-application-of-the-jurisprude/Changing%20the%20Concepts%20of%20Quranic%20Terminology%20as%20an%20Application%20of%20the%20Jurisprudence%20of%20the%20Qur%27anic%20Tongue_djvu.txt",
        category: "quranic_studies",
        ai_access: {
            structured_data: true,
            api_accessible: true,
            content_analysis: true,
            formats: ["html", "pdf", "txt"]
        }
    },
    {
        id: "editing-the-quranic-terminology-tome1",
        title_ar: "تحرير المصطلح القرآني المجلد 1",
        title_en: "Editing the Qur'anic Term - Tome 1",
        path_ar: "https://drive.google.com/file/d/1XiDWZeVCDfbj-1HjSD3hwwYlt7oJYDQB/view?usp=sharing",
        path_en: "https://drive.google.com/file/d/1sgjofHSV_Mua6G1p_zI3zEZwN5Ue4qvM/view?usp=sharing",
        pdf_ar: "https://dn721201.ca.archive.org/0/items/1_20250722_20250722_1041/%D8%AA%D8%AD%D8%B1%D9%8A%D8%B1%20%D8%A7%D9%84%D9%85%D8%B5%D8%B7%D9%84%D8%AD%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%20%D8%AF%D8%B1%D8%A7%D8%B3%D8%A9%20%D8%AA%D8%B7%D8%A8%D9%8A%D9%82%D9%8A%D8%A9%20%D9%81%D9%8A%20%D9%81%D9%82%D9%87%20%D8%A7%D9%84%D9%84%D8%B3%D8%A7%D9%86%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%20%D8%A7%D9%84%D9%85%D8%AC%D9%84%D8%AF%201.pdf",
        pdf_en: "https://ia801502.us.archive.org/7/items/editing-the-qur-anic-term-an-applied-study-in-the-jurisprudence-of-the-qur-anic-/EDITING%20THE%20QUR%27ANIC%20TERM%20-%20AN%20APPLIED%20STUDY%20IN%20THE%20JURISPRUDENCE%20OF%20THE%20QUR%27ANIC%20TONGUE%20Tome%201%20translate%20by%20google.pdf",
        text_ar: "https://archive.org/stream/1_20250722_20250722_1041/%D8%AA%D8%AD%D8%B1%D9%8A%D8%B1%20%D8%A7%D9%84%D9%85%D8%B5%D8%B7%D9%84%D8%AD%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%20%D8%AF%D8%B1%D8%A7%D8%B3%D8%A9%20%D8%AA%D8%B7%D8%A8%D9%8A%D9%82%D9%8A%D8%A9%20%D9%81%D9%8A%20%D9%81%D9%82%D9%87%20%D8%A7%D9%84%D9%84%D8%B3%D8%A7%D9%86%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%20%D8%A7%D9%84%D9%85%D8%AC%D9%84%D8%AF%201_djvu.txt",
        text_en: "https://archive.org/stream/editing-the-qur-anic-term-an-applied-study-in-the-jurisprudence-of-the-qur-anic-/EDITING%20THE%20QUR%27ANIC%20TERM%20-%20AN%20APPLIED%20STUDY%20IN%20THE%20JURISPRUDENCE%20OF%20THE%20QUR%27ANIC%20TONGUE%20Tome%201%20translate%20by%20google_djvu.txt",
        category: "quranic_studies",
        ai_access: {
            structured_data: true,
            api_accessible: true,
            content_analysis: true,
            formats: ["html", "pdf", "txt"]
        }
    },
    {
        id: "editing-the-quranic-terminology-tome2",
        title_ar: "تحرير المصطلح القرآني المجلد 2",
        title_en: "Editing the Qur'anic Term - Tome 2",
        path_ar: "https://drive.google.com/file/d/1k4xsrT408I7tT7xY-h4VmQE-v301Gx0C/view?usp=sharing",
        path_en: "https://drive.google.com/file/d/1Gqr8YJzAOp2QFRIrVMW-c0vASf8x4uzP/view?usp=sharing",
        pdf_ar: "https://ia801901.us.archive.org/10/items/2_20250724_20250724_0836/%D8%AA%D8%AD%D8%B1%D9%8A%D8%B1%20%D8%A7%D9%84%D9%85%D8%B5%D8%B7%D9%84%D8%AD%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%20%20%D8%AF%D8%B1%D8%A7%D8%B3%D8%A9%20%D8%AA%D8%B7%D8%A8%D9%8A%D9%82%D9%8A%D8%A9%20%D9%81%D9%8A%20%D9%81%D9%82%D9%87%20%D8%A7%D9%84%D9%84%D8%B3%D8%A7%D9%86%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%20%D8%A7%D9%84%D9%85%D8%AC%D9%84%D8%AF%202.pdf",
        pdf_en: "https://dn721608.ca.archive.org/0/items/editing-the-qur-anic-term-an-applied-study-in-the-jurisprudence-of-the-qur-anic-_202508/EDITING%20THE%20QUR%27ANIC%20TERM%20-%20AN%20APPLIED%20STUDY%20IN%20THE%20JURISPRUDENCE%20OF%20THE%20QUR%27ANIC%20TONGUE%20Tome%202%20translate%20by%20google.pdf",
        text_ar: "https://archive.org/stream/2_20250724_20250724_0836/%D8%AA%D8%AD%D8%B1%D9%8A%D8%B1%20%D8%A7%D9%84%D9%85%D8%B5%D8%B7%D9%84%D8%AD%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%20%20%D8%AF%D8%B1%D8%A7%D8%B3%D8%A9%20%D8%AA%D8%B7%D8%A8%D9%8A%D9%82%D9%8A%D8%A9%20%D9%81%D9%8A%20%D9%81%D9%82%D9%87%20%D8%A7%D9%84%D9%84%D8%B3%D8%A7%D9%86%20%D8%A7%D9%84%D9%82%D8%B1%D8%A2%D9%86%D9%8A%20%D8%A7%D9%84%D9%85%D8%AC%D9%84%D8%AF%202_djvu.txt",
        text_en: "https://archive.org/stream/editing-the-qur-anic-term-an-applied-study-in-the-jurisprudence-of-the-qur-anic-_202508/EDITING%20THE%20QUR%27ANIC%20TERM%20-%20AN%20APPLIED%20STUDY%20IN%20THE%20JURISPRUDENCE%20OF%20THE%20QUR%27ANIC%20TONGUE%20Tome%202%20translate%20by%20google_djvu.txt",
        category: "quranic_studies",
        ai_access: {
            structured_data: true,
            api_accessible: true,
            content_analysis: true,
            formats: ["html", "pdf", "txt"]
        }
    },
    {
        id: "and-so-that-he-may-be-of-the-certain-ones",
        title_ar: "وليكون من الموقنين: دراسة في فلسفة الإيمان بالغيب",
        title_en: "And So That He May Be of the Certain Ones: A Study in the Philosophy of Faith in the Unseen",
        path_ar: "https://drive.google.com/file/d/1T5Rj8S9T0U1V2W3X4Y5Z6A7B8C9D0E1F/view?usp=sharing",
        path_en: "https://drive.google.com/file/d/1G2H3I4J5K6L7M8N9O0P1Q2R3S4T5U6V7/view?usp=sharing",
        pdf_ar: "https://dn721406.ca.archive.org/0/items/and-so-that-he-may-be-of-the-certain-ones-a-study-in-the-philosophy-of-faith-in-the-unseen/%D9%88%D9%84%D9%8A%D9%83%D9%88%D9%86%20%D9%85%D9%86%20%D8%A7%D9%84%D9%85%D9%88%D9%82%D9%86%D9%8A%D9%86%20%D8%AF%D8%B1%D8%A7%D8%B3%D8%A9%20%D9%81%D9%8A%20%D9%81%D9%84%D8%B3%D9%81%D8%A9%20%D8%A7%D9%84%D8%A5%D9%8A%D9%85%D8%A7%D9%86%20%D8%A8%D8%A7%D9%84%D8%BA%D9%8A%D8%A8.pdf",
        pdf_en: "https://ia800208.us.archive.org/12/items/and-so-that-he-may-be-of-the-certain-ones-a-study-in-the-philosophy-of-faith-in-the-unseen/AND%20SO%20THAT%20HE%20MAY%20BE%20OF%20THE%20CERTAIN%20ONES%20-%20A%20STUDY%20IN%20THE%20PHILOSOPHY%20OF%20FAITH%20IN%20THE%20UNSEEN.pdf",
        text_ar: "https://archive.org/stream/and-so-that-he-may-be-of-the-certain-ones-a-study-in-the-philosophy-of-faith-in-the-unseen/%D9%88%D9%84%D9%8A%D9%83%D9%88%D9%86%20%D9%85%D9%86%20%D8%A7%D9%84%D9%85%D9%88%D9%82%D9%86%D9%8A%D9%86%20%D8%AF%D8%B1%D8%A7%D8%B3%D8%A9%20%D9%81%D9%8A%20%D9%81%D9%84%D8%B3%D9%81%D8%A9%20%D8%A7%D9%84%D8%A5%D9%8A%D9%85%D8%A7%D9%86%20%D8%A8%D8%A7%D9%84%D8%BA%D9%8A%D8%A8_djvu.txt",
        text_en: "https://archive.org/stream/and-so-that-he-may-be-of-the-certain-ones-a-study-in-the-philosophy-of-faith-in-the-unseen/AND%20SO%20THAT%20HE%20MAY%20BE%20OF%20THE%20CERTAIN%20ONES%20-%20A%20STUDY%20IN%20THE%20PHILOSOPHY%20OF%20FAITH%20IN%20THE%20UNSEEN_djvu.txt",
        category: "faith_studies",
        ai_access: {
            structured_data: true,
            api_accessible: true,
            content_analysis: true,
            formats: ["html", "pdf", "txt"]
        }
    },
    {
        id: "names-in-the-holy",
        title_ar: "الأسماء الحسنى الوظيفية",
        title_en: "The Functional Beautiful Names",
        path_ar: "https://drive.google.com/file/d/1N2o3p4q5r6t7u8v9w0x1y2z3a4b5c6d7/view?usp=sharing",
        path_en: "https://drive.google.com/file/d/1oPq4r5s6t7u8v9w0x1y2z3a4b5c6d7e8/view?usp=sharing",
        pdf_ar: "https://ia801602.us.archive.org/1/items/20250707_20250707_0955/%D8%A7%D9%84%D8%A3%D8%B3%D9%85%D8%A7%D8%A1%20%D8%A7%D9%84%D8%AD%D8%B3%D9%86%D9%89%20%D8%A7%D9%84%D9%88%D8%B8%D9%8A%D9%81%D9%8A%D8%A9%20%D8%AF%D8%B1%D8%A7%D8%B3%D8%A9%20%D8%AA%D9%88%D9%82%D9%8A%D9%81%D9%8A%D8%A9%20%D8%AA%D8%AD%D9%84%D9%8A%D9%84%D9%8A%D8%A9%20%D9%84%D8%AF%D9%84%D8%A7%D9%84%D8%A7%D8%AA%20%D8%A7%D9%84%D8%AA%D8%AF%D8%A8%D9%8A%D8%B1%20%D8%A7%D9%84%D8%A5%D9%84%D9%87%D9%8A.pdf",
        pdf_en: "https://ia801704.us.archive.org/3/items/the-functional-beautiful-names-an-analytical-discretionary-study-of-the-connotations-of-divine-management/The%20Functional%20Beautiful%20Names%20-%20An%20Analytical%20Discretionary%20Study%20of%20the%20Connotations%20of%20Divine%20Management.pdf",
        text_ar: "https://archive.org/stream/20250707_20250707_0955/%D8%A7%D9%84%D8%A3%D8%B3%D9%85%D8%A7%D8%A1%20%D8%A7%D9%84%D8%AD%D8%B3%D9%86%D9%89%20%D8%A7%D9%84%D9%88%D8%B8%D9%8A%D9%81%D9%8A%D8%A9%20%D8%AF%D8%B1%D8%A7%D8%B3%D8%A9%20%D8%AA%D9%88%D9%82%D9%8A%D9%81%D9%8A%D8%A9%20%D8%AA%D8%AD%D9%84%D9%8A%D9%84%D9%8A%D8%A9%20%D9%84%D8%AF%D9%84%D8%A7%D9%84%D8%A7%D8%AA%20%D8%A7%D9%84%D8%AA%D8%AF%D8%A8%D9%8A%D8%B1%20%D8%A7%D9%84%D8%A5%D9%84%D9%87%D9%8A_djvu.txt",
        text_en: "https://archive.org/stream/the-functional-beautiful-names-an-analytical-discretionary-study-of-the-connotations-of-divine-management/The%20Functional%20Beautiful%20Names%20-%20An%20Analytical%20Discretionary%20Study%20of%20the%20Connotations%20of%20Divine%20Management_djvu.txt",
        category: "faith_studies",
        ai_access: {
            structured_data: true,
            api_accessible: true,
            content_analysis: true,
            formats: ["html", "pdf", "txt"]
        }
    },
    {
        id: "prostration-and-glorification-in-the-qur’an",
        title_ar: "السجود والتسبيح في القرآن: من التنزيه القلبي إلى الخضوع العملي",
        title_en: "Prostration and Glorification in the Qur’an: From Heartfelt Purification to Practical Submission",
        path_ar: "https://drive.google.com/file/d/1SMFzP3qbsclWGaYJH_idtBPC2HOlZBuB/view?usp=sharing",
        path_en: "https://drive.google.com/file/d/1LgKEAcmmtIql5jFdRF4kZc0Xow-dPWjd/view?usp=sharing",
        pdf_ar: "https://drive.google.com/uc?export=download&id=1SMFzP3qbsclWGaYJH_idtBPC2HOlZBuB",
        pdf_en: "https://drive.google.com/uc?export=download&id=1LgKEAcmmtIql5jFdRF4kZc0Xow-dPWjd",
        text_ar: "https://drive.google.com/uc?export=download&id=1Ic6Us2cmPScuJPOYUzShq-GERNdXO-gx",
        text_en: "https://drive.google.com/uc?export=download&id=1-4pwIbiwFemrRSoMqGDGCgmPtEkiTlXD",
        category: "faith_studies",
        ai_access: {
            structured_data: true,
            api_accessible: true,
            content_analysis: true,
            formats: ["html", "pdf", "txt"]
        }
    },
    {
        id: "christ-and-mary-in-the-qur’an",
        title_ar: "المسيح ومريم في القرآن: من الرمز الباطني إلى النموذج الإنساني",
        title_en: "Christ and Mary in the Qur’an: From the Esoteric Symbol to the Human Model",
        path_ar: "https://drive.google.com/file/d/1tg6hiu3rJs1AClr-rfT732y2zN6-cHmJ/view?usp=sharing",
        path_en: "https://drive.google.com/file/d/16r8XSPcI5ShgIvX_7ReHJ7cmFscJ6v_t/view?usp=sharing",
        pdf_ar: "https://drive.google.com/uc?export=download&id=1tg6hiu3rJs1AClr-rfT732y2zN6-cHmJ",
        pdf_en: "https://drive.google.com/uc?export=download&id=16r8XSPcI5ShgIvX_7ReHJ7cmFscJ6v_t",
        text_ar: "https://drive.google.com/uc?export=download&id=12xfvS3lrXzU5EPijQGWWThmxoRPOdMDZ",
        text_en: "https://drive.google.com/uc?export=download&id=1YtX1Q9rjzo-qL6UXCDeklHUcjuKe9m6w",
        category: "faith_studies",
        ai_access: {
            structured_data: true,
            api_accessible: true,
            content_analysis: true,
            formats: ["html", "pdf", "txt"]
        }
    }
];

// دالة لتحميل وعرض الكتب
function loadBooks() {
    const bookGrid = document.getElementById('book-grid');
    const newBookGrid = document.getElementById('new-book-grid');
    bookGrid.innerHTML = '';
    newBookGrid.innerHTML = '';
    
    // إضافة الكتب الجديدة أولاً
    const newBooks = libraryBooks.slice(0, 6);
    newBooks.forEach(book => {
        const bookCard = createBookCard(book, true);
        newBookGrid.appendChild(bookCard);
    });
    
    // إضافة جميع الكتب
    libraryBooks.forEach(book => {
        const bookCard = createBookCard(book, false);
        bookGrid.appendChild(bookCard);
    });
    
    // تحديث عدد الكتب
    document.getElementById('total-books-count').textContent = libraryBooks.length * 2;
    document.getElementById('new-books-count').textContent = newBooks.length * 2;
}

// دالة لإنشاء بطاقة كتاب
function createBookCard(book, isNew) {
    const bookCard = document.createElement('div');
    bookCard.className = 'book-card';
    bookCard.setAttribute('data-lang', 'ar');
    bookCard.setAttribute('data-category', book.category);
    bookCard.setAttribute('data-ai-access', JSON.stringify(book.ai_access));
    bookCard.id = `book-${book.id}-ar`;
    
    const newBadge = isNew ? '<span class="new-badge-card">جديد</span>' : '';
    const aiBadge = '<span class="ai-badge">🤖 متوافق مع الذكاء الاصطناعي</span>';
    
    bookCard.innerHTML = `
        <div class="book-cover">
            ${newBadge}
            ${aiBadge}
            <img src="assets/images/covers/${book.id}-ar.png" 
                 alt="غلاف ${book.title_ar}"
                 loading="lazy"
                 width="250"
                 height="200">
        </div>
        <div class="book-info">
            <h2>${book.title_ar}</h2>
            <p class="book-meta">تأليف: ناصر ابن داوود</p>
            <p class="book-desc">${getBookDescription(book.id)}</p>
            <div class="book-formats">
                <span>📖 HTML</span>
                <span>📄 PDF</span>
                <span>📝 TXT</span>
            </div>
            <div class="book-actions">
                <a href="${book.path_ar}" class="btn">النسخة العربية</a>
                <a href="${book.path_en}" class="btn btn-outline">English Version</a>
            </div>
            <div class="ai-access-links">
                <a href="${book.text_ar}" download>تحميل النص الخام</a>
                <a href="${book.pdf_ar}" download>تحميل PDF العربية</a>
                <a href="${book.pdf_en}" download>Download English PDF</a>
                <a href="api/ai-access/metadata/${book.id}.json">بيانات الذكاء الاصطناعي</a>
            </div>
        </div>
    `;
    
    return bookCard;
}

// دالة للحصول على وصف الكتاب
function getBookDescription(bookId) {
    const descriptions = {
        "conscious-contemplation": "كتاب يشرح منهجية التدبر العميق للقرآن الكريم وتطبيقاته العصرية",
        "anwar-al-bayan": "دراسة علمية للرسم العثماني وأسراره اللغوية",
        "changing-the-concepts": "دراسة تطبيقية لفقه اللسان القرآني وتحليل المصطلحات القرآنية",
        "editing-the-quranic-terminology-tome1": "دراسة تطبيقية في فقه اللسان القرآني، المجلد الأول",
        "editing-the-quranic-terminology-tome2": "دراسة تطبيقية في فقه اللسان القرآني، المجلد الثاني",
        "editing-the-quranic-terminology-tome3": "دراسة تطبيقية في فقه اللسان القرآني، المجلد الثالث",
        "contemplation-in-the-mirror": "تطبيقات عملية للمخطوطات الرقمية في تدبر القرآن الكريم",
        "the-jurisprudence": "دراسة منهجية لفهم اللسان العربي القرآني ومنهجية تدبر النص الإلهي",
        "digitizing": "دراسة منهجية لحفظ النص القرآني رقمياً وتطبيقاته",
        "modesty": "دراسة معمقة للحياء كأداة معرفية وأخلاقية في فهم القرآن الكريم",
        "malakoot": "رحلة برهانية في ملكوت السماوات والأرض وما بينهما",
        "names-in-the-holy": "دراسة توقيفية تحليلية لدلالات التدبير الإلهي من خلال الأسماء الحسنى",
        "prostration-and-glorification-in-the-qur’an": "دراسة معمقة للسجود والتسبيح في القرآن الكريم من التنزيه القلبي إلى الخضوع العملي",
        "christ-and-mary-in-the-qur’an": "دراسة تحليلية لشخصيتي المسيح ومريم في القرآن الكريم من الرمز الباطني إلى النموذج الإنساني"
    };
    
    return descriptions[bookId] || "مؤلف قيم في علوم القرآن واللغة";
}

// تحديث وقت التحديث الأخير
function updateLastUpdateTime() {
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.getElementById('last-update').textContent = now.toLocaleDateString('ar-SA', options);
}

// إعداد الفلاتر المتقدمة
function setupAdvancedFilters() {
    const contentType = document.getElementById('content-type');
    const aiCompatibility = document.getElementById('ai-compatibility');
    
    const applyFilters = () => {
        const contentValue = contentType.value;
        const aiValue = aiCompatibility.value;
        
        document.querySelectorAll('.book-card').forEach(card => {
            const category = card.getAttribute('data-category');
            const aiAccess = JSON.parse(card.getAttribute('data-ai-access'));
            
            let contentMatch = contentValue === 'all' || category === contentValue;
            let aiMatch = aiValue === 'all' || 
                         (aiValue === 'structured' && aiAccess.structured_data) ||
                         (aiValue === 'api' && aiAccess.api_accessible) ||
                         (aiValue === 'analysis' && aiAccess.content_analysis);
            
            card.style.display = contentMatch && aiMatch ? 'block' : 'none';
        });
    };
    
    contentType.addEventListener('change', applyFilters);
    aiCompatibility.addEventListener('change', applyFilters);
}

// دالة لإعداد أزرار التصفية
function setupFilterButtons() {
    document.querySelectorAll('.filter-btn').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const category = button.getAttribute('data-category');
            document.querySelectorAll('.book-card').forEach(card => {
                card.style.display = category === 'all' || card.getAttribute('data-category') === category ? 'block' : 'none';
            });
        });
    });
}

// دالة لإعداد تصفية الكتب الجديدة
function setupNewBooksFilter() {
    const newBooksToggle = document.getElementById('new-books-toggle');
    newBooksToggle.addEventListener('change', () => {
        const bookGrid = document.getElementById('book-grid');
        const newBookGrid = document.getElementById('new-book-grid');
        if (newBooksToggle.checked) {
            bookGrid.style.display = 'none';
            newBookGrid.style.display = 'grid';
        } else {
            bookGrid.style.display = 'grid';
            newBookGrid.style.display = 'none';
        }
    });
}

// تهيئة الصفحة عند التحميل
document.addEventListener('DOMContentLoaded', function() {
    updateLastUpdateTime();
    loadBooks();
    setupFilterButtons();
    setupNewBooksFilter();
    setupAdvancedFilters();
    
    // تحديث العد تلقائياً كل ساعة
    setInterval(() => {
        updateLastUpdateTime();
    }, 3600000);
});
