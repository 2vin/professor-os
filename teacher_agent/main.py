import argparse
import sys

if sys.version_info < (3, 7) or sys.version_info >= (3, 8):
    print('WARNING: This build is intended for Python 3.7.x. Detected: %s' % sys.version.split()[0])

from .config import settings
from .pipeline import RoboticsTeacherAgent
from .runtime import monitor
from .scheduler import DailyISTScheduler
from .source_sync import SourceSyncWatcher


def run():
    try:
        result = RoboticsTeacherAgent().run_once()
        print(result)
        return result
    except Exception as exc:
        print('Teacher agent failed: {0}'.format(exc), file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='Generate/publish one class and exit.')
    parser.add_argument('--scheduler', action='store_true', help='Run the nightly IST scheduler without the website.')
    parser.add_argument('--dashboard', action='store_true', help='Run the local Professor OS website explicitly.')
    args = parser.parse_args()

    if args.once:
        result = run()
        sys.exit(0 if result else 1)

    if args.scheduler:
        source_watcher = SourceSyncWatcher() if settings.auto_sync_source else None
        if source_watcher:
            source_watcher.start()
        scheduler = DailyISTScheduler(run, hour=settings.nightly_release_hour, minute=settings.nightly_release_minute)
        scheduler.start()
        print('Robotics Teacher Agent scheduled daily at {0:02d}:{1:02d} (Asia/Kolkata)'.format(settings.nightly_release_hour, settings.nightly_release_minute))
        try:
            while True:
                import time
                time.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            scheduler.stop()
            if source_watcher:
                source_watcher.stop()
        return

    from .dashboard import run_dashboard
    run_dashboard()


if __name__ == '__main__':
    main()
