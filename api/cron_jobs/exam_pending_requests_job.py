from django_cron import CronJobBase, Schedule
from ..models import ExamPendingRequest, Exam, ExamVideo
from django.core.files import File
import os
from ..video_utils import MKV2OGGTranscoder, MKV2MP4Transcoder, MKV2WEBMTranscoder
from pathlib import Path
import logging


class ExamPendingRequestsJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every minute
    CHUNK_SIZE = 10 * 1024 * 1024

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'api.ExamPendingRequestsJob'  # a unique code

    def do(self):
        logger = logging.getLogger('cronjobs')
        pending_exams = ExamPendingRequest.objects.filter(is_processed=False)
        for pending_exam in pending_exams:
            # create exam
            video_duration_seconds = pending_exam.duration
            exam = Exam()
            exam.taker = pending_exam.taker
            exam.exercise = pending_exam.exercise
            exam.device = pending_exam.device
            exam.duration = video_duration_seconds
            exam.save()
            logger.info("ExamPendingRequestsJob - new exam created")

            for pending_video in pending_exam.videos.all():
                file_name = pending_video.file.path
                logger.info("ExamPendingRequestsJob - processing file {name}".format(name=file_name))

                # transcoding

                logger.info(
                    "ExamPendingRequestsJob - doing transcoding of file {tmp_name} duration {seconds} seconds".format(
                        tmp_name=file_name,
                        seconds=video_duration_seconds))
                # ogg

                output_file_ogg = os.path.splitext(file_name)[0] + '.ogg'
                logger.info("ExamPendingRequestsJob - start trascoding of file {tmp_name} to {output_file_ogg}".format(
                    tmp_name=file_name,
                    output_file_ogg=output_file_ogg))
                t1 = MKV2OGGTranscoder(file_name, output_file_ogg)
                t1.apply()
                logger.info("ExamPendingRequestsJob - finishing ogg trascoding")
                # webm
                output_file_webm = os.path.splitext(file_name)[0] + '.webm'
                logger.info("ExamPendingRequestsJob - start trascoding of file {tmp_name} to {output_file_webm}".format(
                    tmp_name=file_name,
                    output_file_webm=output_file_webm))

                t2 = MKV2WEBMTranscoder(file_name, output_file_webm)
                t2.apply()
                logger.info("ExamPendingRequestsJob - finishing webm trascoding")
                # mp4
                output_file_mp4 = os.path.splitext(file_name)[0] + '.mp4'
                logger.info("ExamPendingRequestsJob - start trascoding of file {tmp_name} to {output_file_mp4}".format(
                    tmp_name=file_name,
                    output_file_mp4=output_file_mp4))

                t3 = MKV2MP4Transcoder(file_name, output_file_mp4)
                t3.apply()
                logger.info("ExamPendingRequestsJob - finishing mp4 trascoding")

                # video 1
                video1 = ExamVideo()
                with open(output_file_ogg, "rb") as file1:
                    django_file1 = File(file1)
                    video1.exam = exam
                    video1.type = "video/ogg"
                    video1.author = pending_exam.taker
                    video1.file.save(Path(output_file_ogg).name, django_file1, save=True)
                    video1.save()
                    logger.info("ExamPendingRequestsJob - saved video OGG")
                # video 2
                video2 = ExamVideo()
                with open(output_file_webm, "rb") as file2:
                    django_file2 = File(file2)
                    video2.exam = exam
                    video2.type = "video/webm"
                    video2.author = pending_exam.taker
                    video2.file.save(Path(output_file_webm).name, django_file2, save=True)
                    video2.save()
                    logger.info("ExamPendingRequestsJob - saved video WEBM")
                # video 3
                video3 = ExamVideo()
                with open(output_file_mp4, "rb") as file3:
                    django_file3 = File(file3)
                    video3.exam = exam
                    video3.type = "video/mp4"
                    video3.author = pending_exam.taker
                    video3.file.save(Path(output_file_mp4).name, django_file3, save=True)
                    video3.save()
                    logger.info("ExamPendingRequestsJob - saved video mp4")

                # removing tmp files
                logger.info("ExamPendingRequestsJob - removing temp files...")
                os.remove(output_file_webm)
                os.remove(output_file_ogg)
                os.remove(output_file_mp4)
                pending_video.delete()
                if os.path.exists(file_name):
                    os.remove(file_name)

            pending_exam.delete()
