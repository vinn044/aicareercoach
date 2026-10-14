#start 
cd ~/Desktop/aicoachSP/aicareercoach

#activate python environments
source .venv/bin/activate

#check branch
git branch

#open terminal 1 for backend
python -m uvicorn backend.main:app --reload

#start terminal 2 for frontend
cd ~/Desktop/aicoachSP/aicareercoach/frontend
npm run dev