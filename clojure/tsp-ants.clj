; Clojure TSP solver using Ant Colony Optimization
; Rich Hickey

;command line for script use, replace 10 below with the number of ants/threads you desire
;java -server -cp clojure.jar clojure.lang.Script tsp-ants.clj -- 10

;basic naive Ant System implementation - see Dorigo et al 1996

(import '(java.util.concurrent.atomic AtomicLong))

;this file defines coords and optimal-tour
(load-file "tsp-data.clj")

(defn distance [coords edge]
  (let [a (coords (first edge)), b (coords (second edge))
        dx (- (:x a) (:x b)), dy (- (:y a) (:y b))
        rxy (Math/sqrt (+ (* dx dx) (* dy dy)))
        txy (int rxy)]
    (if (< txy rxy) (inc txy) txy)))

(def Q 100.0)
(def INIT-P 0.5)
(def P-FACTOR 1.0)
(def D-FACTOR 5.0)
(def E-FACTOR 0.5)

(defn tour-length [tour]
  (reduce + (map #(distance coords %) (map set (partition 2 1 tour)))))

(def optimal-distance 100)

(def nodes (set (keys coords)))
(def edges (set (for [a nodes b nodes :when (not= a b)] #{a b})))
(def distances (reduce (fn [m e] (assoc m e (distance coords e))) {} edges))
(def pheromones (into {} (map #(vector % (ref INIT-P)) edges))) 

(defn prob [edge]
  (* (Math/pow @(pheromones edge) P-FACTOR) 
     (Math/pow (/ 1.0 (distances edge)) D-FACTOR)))

(def probs (reduce (fn [m e] (assoc m e (ref (prob e)))) {} edges))

(def best-length (ref Integer/MAX_VALUE))
(def best-tour (ref Integer/MAX_VALUE))
(def #^AtomicLong tour-count (AtomicLong.))

(def ants (ref nil))
(def running true)

(def evaporator (agent 0))

(defn tick-action [cnt]
  (let [new-cnt (inc cnt)]
    (when (zero? (rem new-cnt (count @ants)))
      (doseq p (vals pheromones)
        (dosync (alter p * E-FACTOR))))
    new-cnt))

(defn wrand 
  "Given a vector of slice sizes, returns the index of a slice given a
  random spin of a roulette wheel with compartments proportional to slices."
  [slices]
  (let [total (reduce + slices), r (rand total)]
    (loop [i 0, sum 0]
      (let [newsum (+ (slices i) sum)]
        (if (< r newsum) i (recur (inc i) newsum))))))

(defn get-prob [from to] @(probs #{from to}))

(defn next-stop [node togo]
  (nth (seq togo) (wrand (vec (map get-prob (repeat node) togo)))))

(defn tour []
  (let [home (rand-int (count nodes))
        togo (disj nodes home)]
    (loop [node home, path [], togo togo]
      (if (empty? togo)
        (conj path home)
        (let [next (next-stop node togo)]
          (recur next (conj path node) (disj togo next)))))))

(defn brag [len tour]
  (println "new best, distance:" len)
  (prn tour))

(defn tour-loop [_]
  (when running
    (let [t (tour)
          len (tour-length t)]
      ;drop pheromones, recalc edge probs
      (doseq edge (map set (partition 2 1 t))
        (dosync 
         (alter (pheromones edge) + (/ Q len))
         (ref-set (probs edge) (prob edge))))
      ;are we the new best?
      (when (< len @best-length)
        (dosync
         (when (< len @best-length)
           (ref-set best-length len)
           (ref-set best-tour t)))
        (brag len t))
      ;counters, evap
      (.incrementAndGet tour-count)
      (send evaporator tick-action)
      (send-off *agent* #'tour-loop)
      nil)))

(defn run [nants]
  (dosync (ref-set ants (map agent (take nants (repeat nil)))))
  (doseq ant @ants
    (send-off ant tour-loop))
  :running)

(defn run-loop  [nants]
  (run nants)
  (println "Running...")
  (let [start (System/currentTimeMillis)]
    (loop []
      (when running
        (Thread/sleep 4000)
        (let [secs (/ (- (System/currentTimeMillis) start) 1000.0)]
          (println "Running" (count nodes) "nodes," nants "ants," tour-count "tours," secs "seconds," 
                   (/ (int (* (/ tour-count secs) 100)) 100.0) "per second, best-so-far:" @best-length 
                   "optimal:" optimal-distance))
        (dorun (map deref @ants))
        (recur)))))

(comment
;repl use
(load-file "tsp-ants.clj")    
(run-loop 10)
;to stop it
(def running false)
)    

;for script use
(when *command-line-args*
  (run-loop (Integer/parseInt (first *command-line-args*))))

