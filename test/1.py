# 1. Base Class สำหรับสื่อการเรียนรู้
class Media:
    def __init__(self, name, extension):
        self.name = name
        self.extension = extension

    def open_media(self):
        pass

# 2. Subclasses สำหรับวิดีโอคอร์สเรียน (.mp4, .mkv, .webm)
class MP4(Media):
    def __init__(self, name):
        super().__init__(name, extension='mp4')
        
    def open_media(self):
        print(f"▶️ [Video Player] Decoding and playing .mp4: {self.name}")

class MKV(Media):
    def __init__(self, name):
        super().__init__(name, extension='mkv')
        
    def open_media(self):
        print(f"▶️ [Video Player] Decoding and playing .mkv: {self.name}")

# Subclasses สำหรับเอกสารประกอบการเรียน (.pdf, .epub, .docx)
class PDF(Media):
    def __init__(self, name, chapter_no):
        super().__init__(name, extension='pdf')
        self.chapter_no = chapter_no
        
    def open_media(self):
        print(f"📖 [PDF Reader] Rendering document .pdf: Chapter {self.chapter_no} - {self.name}")

class EPUB(Media):
    def __init__(self, name, chapter_no):
        super().__init__(name, extension='epub')
        self.chapter_no = chapter_no
        
    def open_media(self):
        print(f"📖 [E-Book Reader] Rendering document .epub: Chapter {self.chapter_no} - {self.name}")

# 3. คลาสสำหรับจัดกลุ่มสื่อการเรียนรู้
class Subject:
    def __init__(self, subject_name, instructor_name):
        self.subject_name = subject_name
        self.instructor_name = instructor_name
        self.video_list = [] # Aggregation: บรรจุ Media

    def add_video(self, video_media):
        self.video_list.append(video_media)

    def open_all(self):
        print(f"\n--- Opening all videos in subject: {self.subject_name} ---")
        for video in self.video_list:
            video.open_media() # Polymorphism

class BookReference:
    def __init__(self, book_name, author):
        self.book_name = book_name
        self.author = author
        self.document_list = [] # Aggregation: บรรจุ Media

    def add_document(self, document_media):
        self.document_list.append(document_media)

class PersonalCollection:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.media_list = [] # บรรจุได้ทั้ง Video และ Document

    def add_media(self, media):
        self.media_list.append(media)

    def open_all(self):
        print(f"\n--- Opening collection: {self.collection_name} ---")
        for media in self.media_list:
            media.open_media() # Polymorphism

# 4. ระบบจัดการส่วนกลาง
class LearningManager:
    def __init__(self):
        self.subjects = []
        self.books = []
        self.collections = []

    def add_subject(self, subject):
        self.subjects.append(subject)

    def add_book(self, book):
        self.books.append(book)

    def add_collection(self, collection):
        self.collections.append(collection)

    def open_subject(self, subject_name):
        for subject in self.subjects:
            if subject.subject_name == subject_name:
                subject.open_all()
                break

    def open_collection(self, collection_name):
        for collection in self.collections:
            if collection.collection_name == collection_name:
                collection.open_all()
                break

    def search_and_open(self, keyword):
        print(f"\n--- Searching for: '{keyword}' ---")
        found = False
        
        # ค้นหาในรายวิชา (ค้นจากชื่อวิชา หรือ ชื่อวิดีโอ)
        for subject in self.subjects:
            if keyword in subject.subject_name:
                subject.open_all()
                found = True
            else:
                for video in subject.video_list:
                    if keyword in video.name:
                        video.open_media()
                        found = True

        # ค้นหาในหนังสืออ้างอิง (ค้นจากชื่อหนังสือ หรือ ชื่อบทเรียน)
        for book in self.books:
            if keyword in book.book_name:
                for doc in book.document_list:
                    doc.open_media()
                found = True
            else:
                for doc in book.document_list:
                    if keyword in doc.name:
                        doc.open_media()
                        found = True
                        
        if not found:
            print("Not found.")